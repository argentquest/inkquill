import re
from pathlib import Path

file_path = Path("tests/integration/care_circle/test_family_membership_integration.py")
content = file_path.read_text(encoding="utf-8")

# 1. Remove _make_client function
content = re.sub(r'def _make_client\(app_instance\):\n(?:    .*\n)*\n', '\n', content)

# 2. Change signatures: remove app_instance from tests that only have client, register_and_login, app_instance
content = content.replace("client, register_and_login, app_instance", "client, register_and_login")

# 3. For tests that don't need to switch back, just use client.cookies.clear()
def simple_repl(match):
    return match.group(0).replace("second_client = _make_client(app_instance)\n    _register(second_client", "client.cookies.clear()\n    _register(client").replace("second_client.", "client.")

content = re.sub(r'def test_join_request_with_valid_code.*?assert "family_name" in data', simple_repl, content, flags=re.DOTALL)
content = re.sub(r'def test_duplicate_join_request_returns_400.*?in resp\.json\(\)\["detail"\]\.lower\(\)', simple_repl, content, flags=re.DOTALL)

# 4. For tests that need to switch back to owner:
# test_owner_can_list_join_requests
def list_reqs_repl(match):
    s = match.group(0)
    s = s.replace("second_client = _make_client(app_instance)\n    _register(second_client, \"req_list_member\")\n    second_client.post",
                  "owner_cookies = dict(client.cookies)\n    client.cookies.clear()\n    _register(client, \"req_list_member\")\n    client.post")
    s = s.replace('resp = client.get("/api/v1/care-circle/family/join-requests")',
                  'client.cookies.clear()\n    client.cookies.update(owner_cookies)\n    resp = client.get("/api/v1/care-circle/family/join-requests")')
    return s
content = re.sub(r'def test_owner_can_list_join_requests.*?assert "username" in data\[0\]', list_reqs_repl, content, flags=re.DOTALL)

# test_owner_can_approve_request
def app_reqs_repl(match):
    s = match.group(0)
    s = s.replace("second_client = _make_client(app_instance)\n    _register(second_client, \"req_approve_member\")\n    second_client.post",
                  "owner_cookies = dict(client.cookies)\n    client.cookies.clear()\n    _register(client, \"req_approve_member\")\n    client.post")
    s = s.replace('requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]',
                  'client.cookies.clear()\n    client.cookies.update(owner_cookies)\n    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]')
    return s
content = re.sub(r'def test_owner_can_approve_request.*?assert not any\(r\["id"\] == membership_id for r in after\)', app_reqs_repl, content, flags=re.DOTALL)

# test_owner_can_reject_request
def rej_reqs_repl(match):
    s = match.group(0)
    s = s.replace("second_client = _make_client(app_instance)\n    _register(second_client, \"req_reject_member\")\n    second_client.post",
                  "owner_cookies = dict(client.cookies)\n    client.cookies.clear()\n    _register(client, \"req_reject_member\")\n    client.post")
    s = s.replace('requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]',
                  'client.cookies.clear()\n    client.cookies.update(owner_cookies)\n    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]')
    return s
content = re.sub(r'def test_owner_can_reject_request.*?assert reject_resp\.json\(\)\["data"\]\["status"\] == "rejected"', rej_reqs_repl, content, flags=re.DOTALL)

# test_owner_can_list_members_after_approval
def mem_reqs_repl(match):
    s = match.group(0)
    s = s.replace("second_client = _make_client(app_instance)\n    _register(second_client, \"active_member\")\n    second_client.post",
                  "owner_cookies = dict(client.cookies)\n    client.cookies.clear()\n    _register(client, \"active_member\")\n    client.post")
    s = s.replace('requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]',
                  'client.cookies.clear()\n    client.cookies.update(owner_cookies)\n    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]')
    return s
content = re.sub(r'def test_owner_can_list_members_after_approval.*?assert all\("username" in m for m in members\)', mem_reqs_repl, content, flags=re.DOTALL)

# test_owner_can_remove_member
def rm_reqs_repl(match):
    s = match.group(0)
    s = s.replace("second_client = _make_client(app_instance)\n    _register(second_client, \"remove_member\")\n    second_client.post",
                  "owner_cookies = dict(client.cookies)\n    client.cookies.clear()\n    _register(client, \"remove_member\")\n    client.post")
    s = s.replace('requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]',
                  'client.cookies.clear()\n    client.cookies.update(owner_cookies)\n    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]')
    return s
content = re.sub(r'def test_owner_can_remove_member.*?assert not any\(m\["id"\] == membership_id for m in members\)', rm_reqs_repl, content, flags=re.DOTALL)


# 5. Admins
def admin_repl(match):
    s = match.group(0)
    s = s.replace("def _register_admin(app_instance, run_db, prefix=\"admin_fam\"):", "def _register_admin(client, run_db, prefix=\"admin_fam\"):")
    s = s.replace("admin_client = _make_client(app_instance)\n    payload, _ = _register(admin_client, prefix)", "client.cookies.clear()\n    payload, _ = _register(client, prefix)")
    s = s.replace("return admin_client", "admin_cookies = dict(client.cookies)\n    return admin_cookies")
    return s
content = re.sub(r'def _register_admin.*?return admin_client', admin_repl, content, flags=re.DOTALL)

content = content.replace("def test_admin_can_list_all_families(client, register_and_login, app_instance, run_db):", "def test_admin_can_list_all_families(client, register_and_login, run_db):")
content = content.replace("def test_admin_can_disable_and_reenable_family(client, register_and_login, app_instance, run_db):", "def test_admin_can_disable_and_reenable_family(client, register_and_login, run_db):")
content = content.replace("def test_admin_can_delete_family(client, register_and_login, app_instance, run_db):", "def test_admin_can_delete_family(client, register_and_login, run_db):")
content = content.replace("def test_disabled_family_blocks_join_requests(client, register_and_login, app_instance, run_db):", "def test_disabled_family_blocks_join_requests(client, register_and_login, run_db):")

# Switch usages of admin_client
content = content.replace('admin_client = _register_admin(app_instance, run_db, "admin_list")', 'admin_cookies = _register_admin(client, run_db, "admin_list")\n    client.cookies.clear()\n    client.cookies.update(admin_cookies)')
content = content.replace('admin_client = _register_admin(app_instance, run_db, "admin_disable")', 'admin_cookies = _register_admin(client, run_db, "admin_disable")\n    client.cookies.clear()\n    client.cookies.update(admin_cookies)')
content = content.replace('admin_client = _register_admin(app_instance, run_db, "admin_delete")', 'admin_cookies = _register_admin(client, run_db, "admin_delete")\n    client.cookies.clear()\n    client.cookies.update(admin_cookies)')
content = content.replace('admin_client = _register_admin(app_instance, run_db, "admin_block")', 'admin_cookies = _register_admin(client, run_db, "admin_block")\n    client.cookies.clear()\n    client.cookies.update(admin_cookies)')

content = content.replace('admin_client.', 'client.')

# test_disabled_family_blocks_join_requests uses member_client = _make_client(app_instance)
content = content.replace('member_client = _make_client(app_instance)\n    _register(member_client, "blocked_member")\n    resp = member_client.post', 'client.cookies.clear()\n    _register(client, "blocked_member")\n    resp = client.post')


file_path.write_text(content, encoding="utf-8")
