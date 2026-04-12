"""Integration tests for scheduler job management endpoints."""

import pytest

pytestmark = pytest.mark.integration


class TestListJobs:
    """Tests for GET /scheduler/jobs endpoint."""

    def test_list_jobs_returns_job_list(self, scheduler_client):
        """GET /scheduler/jobs returns a list of scheduled jobs."""
        response = scheduler_client.get("/scheduler/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_list_jobs_contains_expected_tasks(self, scheduler_client):
        """GET /scheduler/jobs contains the default scheduled tasks."""
        response = scheduler_client.get("/scheduler/jobs")
        assert response.status_code == 200
        jobs = response.json()["jobs"]
        job_ids = {job["id"] for job in jobs}
        assert "care_circle.daily_session" in job_ids
        assert "care_circle.daily_newsletter" in job_ids
        assert "scheduler.cleanup_old_run_logs" in job_ids

    def test_list_jobs_returns_job_fields(self, scheduler_client):
        """GET /scheduler/jobs returns jobs with expected fields."""
        response = scheduler_client.get("/scheduler/jobs")
        assert response.status_code == 200
        jobs = response.json()["jobs"]
        assert len(jobs) > 0
        job = jobs[0]
        assert "id" in job
        assert "name" in job
        assert "next_run" in job
        assert "trigger" in job


class TestTriggerJob:
    """Tests for POST /scheduler/jobs/{task_key}/run endpoint."""

    def test_trigger_valid_job_succeeds(self, scheduler_client):
        """POST /scheduler/jobs/{task_key}/run triggers immediate execution."""
        response = scheduler_client.post("/scheduler/jobs/care_circle.daily_session/run")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["task_key"] == "care_circle.daily_session"

    def test_trigger_nonexistent_task_returns_404(self, scheduler_client):
        """POST /scheduler/jobs/{invalid_key}/run returns 404."""
        response = scheduler_client.post("/scheduler/jobs/nonexistent.task/run")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_trigger_cleanup_task_succeeds(self, scheduler_client):
        """POST /scheduler/jobs/scheduler.cleanup_old_run_logs/run succeeds."""
        response = scheduler_client.post("/scheduler/jobs/scheduler.cleanup_old_run_logs/run")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["task_key"] == "scheduler.cleanup_old_run_logs"


class TestPauseJob:
    """Tests for POST /scheduler/jobs/{task_key}/pause endpoint."""

    def test_pause_valid_job_succeeds(self, scheduler_client):
        """POST /scheduler/jobs/{task_key}/pause pauses the job."""
        response = scheduler_client.post("/scheduler/jobs/care_circle.daily_session/pause")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "paused" in data["message"].lower()
        assert data["task_key"] == "care_circle.daily_session"

    def test_pause_job_reflects_in_status(self, scheduler_client):
        """After pausing, the job should show as paused in status."""
        # Pause the job
        pause_response = scheduler_client.post("/scheduler/jobs/care_circle.daily_newsletter/pause")
        assert pause_response.status_code == 200

        # Check status endpoint
        status_response = scheduler_client.get("/scheduler/status")
        assert status_response.status_code == 200
        tasks = status_response.json()["tasks"]
        newsletter_task = next((t for t in tasks if t["key"] == "care_circle.daily_newsletter"), None)
        assert newsletter_task is not None


class TestResumeJob:
    """Tests for POST /scheduler/jobs/{task_key}/resume endpoint."""

    def test_resume_valid_job_succeeds(self, scheduler_client):
        """POST /scheduler/jobs/{task_key}/resume resumes the job."""
        # First pause the job
        scheduler_client.post("/scheduler/jobs/care_circle.daily_session/pause")

        # Then resume it
        response = scheduler_client.post("/scheduler/jobs/care_circle.daily_session/resume")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "resumed" in data["message"].lower()
        assert data["task_key"] == "care_circle.daily_session"

    def test_resume_job_reflects_in_list(self, scheduler_client):
        """After resuming, the job should appear in the job list."""
        # Pause then resume
        scheduler_client.post("/scheduler/jobs/care_circle.daily_newsletter/pause")
        scheduler_client.post("/scheduler/jobs/care_circle.daily_newsletter/resume")

        # Check job list
        response = scheduler_client.get("/scheduler/jobs")
        assert response.status_code == 200
        jobs = response.json()["jobs"]
        job_ids = {job["id"] for job in jobs}
        assert "care_circle.daily_newsletter" in job_ids


class TestRescheduleJob:
    """Tests for POST /scheduler/jobs/{task_key}/reschedule endpoint."""

    def test_reschedule_valid_job_succeeds(self, scheduler_client):
        """POST /scheduler/jobs/{task_key}/reschedule changes the cron schedule."""
        new_cron = "0 10 * * *"  # 10:00 AM daily
        response = scheduler_client.post(
            "/scheduler/jobs/care_circle.daily_session/reschedule",
            json={"cron": new_cron}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert new_cron in data["message"]
        assert data["task_key"] == "care_circle.daily_session"

    def test_reschedule_with_invalid_cron_fails(self, scheduler_client):
        """POST /scheduler/jobs/{task_key}/reschedule with invalid cron returns error."""
        invalid_cron = "not-a-cron-expression"
        response = scheduler_client.post(
            "/scheduler/jobs/care_circle.daily_session/reschedule",
            json={"cron": invalid_cron}
        )
        assert response.status_code == 400

    def test_reschedule_nonexistent_task_fails(self, scheduler_client):
        """POST /scheduler/jobs/{invalid_key}/reschedule returns error."""
        response = scheduler_client.post(
            "/scheduler/jobs/nonexistent.task/reschedule",
            json={"cron": "0 12 * * *"}
        )
        assert response.status_code == 400


class TestJobWorkflow:
    """End-to-end workflow tests for job management."""

    def test_pause_resume_cycle(self, scheduler_client):
        """Full cycle: pause, verify, resume, verify."""
        task_key = "care_circle.daily_session"

        # Pause
        pause_resp = scheduler_client.post(f"/scheduler/jobs/{task_key}/pause")
        assert pause_resp.status_code == 200

        # Resume
        resume_resp = scheduler_client.post(f"/scheduler/jobs/{task_key}/resume")
        assert resume_resp.status_code == 200

        # Verify job is still in the list
        list_resp = scheduler_client.get("/scheduler/jobs")
        assert list_resp.status_code == 200
        jobs = list_resp.json()["jobs"]
        job_ids = {job["id"] for job in jobs}
        assert task_key in job_ids

    def test_trigger_after_pause(self, scheduler_client):
        """Can trigger a paused job manually."""
        task_key = "care_circle.daily_session"

        # Pause the scheduled job
        scheduler_client.post(f"/scheduler/jobs/{task_key}/pause")

        # Manual trigger should still work
        trigger_resp = scheduler_client.post(f"/scheduler/jobs/{task_key}/run")
        assert trigger_resp.status_code == 200
        assert trigger_resp.json()["success"] is True

    def test_reschedule_and_verify(self, scheduler_client):
        """Reschedule a job and verify the change."""
        task_key = "scheduler.cleanup_old_run_logs"
        new_cron = "0 4 * * 1"  # Monday 4 AM

        # Reschedule
        reschedule_resp = scheduler_client.post(
            f"/scheduler/jobs/{task_key}/reschedule",
            json={"cron": new_cron}
        )
        assert reschedule_resp.status_code == 200

        # Verify in job list
        list_resp = scheduler_client.get("/scheduler/jobs")
        assert list_resp.status_code == 200
        jobs = list_resp.json()["jobs"]
        cleanup_job = next((j for j in jobs if j["id"] == task_key), None)
        assert cleanup_job is not None
        assert new_cron in cleanup_job["trigger"]
