"""
Morning Stretch provider for Care Circle patient sessions.
Delivers a gentle seated stretching exercise from a curated pool.
Static provider — no LLM required.
"""

import random
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


STRETCHES = [
    {
        "title": "Neck Side Stretch",
        "description": "Gently loosen tension in your neck and shoulders.",
        "steps": [
            "Sit up straight in your chair with your feet flat on the floor.",
            "Slowly tilt your right ear toward your right shoulder.",
            "Hold for 5 seconds and feel the gentle stretch on the left side of your neck.",
            "Slowly return to center, then repeat on the left side.",
            "Do this 3 times on each side.",
        ],
    },
    {
        "title": "Shoulder Rolls",
        "description": "Release stiffness in your shoulders with this easy movement.",
        "steps": [
            "Sit comfortably with your hands resting on your lap.",
            "Slowly roll both shoulders forward in a big circle — up, back, and down.",
            "Repeat 5 times forward.",
            "Now reverse — roll your shoulders backward 5 times.",
            "Take a deep breath and relax.",
        ],
    },
    {
        "title": "Seated Ankle Circles",
        "description": "Wake up your feet and ankles with gentle circles.",
        "steps": [
            "Sit with your back straight and feet slightly off the floor.",
            "Lift your right foot and slowly rotate your ankle in a circle — 5 times clockwise.",
            "Then rotate it 5 times counter-clockwise.",
            "Lower your right foot and repeat with your left foot.",
            "This helps with circulation and flexibility.",
        ],
    },
    {
        "title": "Wrist & Hand Warm-Up",
        "description": "Keep your hands and wrists nimble and comfortable.",
        "steps": [
            "Hold both hands out in front of you, palms facing down.",
            "Slowly open your fingers wide, then gently make a soft fist.",
            "Repeat the open-and-close 8 times.",
            "Then gently rotate your wrists in circles — 5 times each direction.",
            "Shake out your hands softly when you are done.",
        ],
    },
    {
        "title": "Upper Back Stretch",
        "description": "Ease tension across your upper back and chest.",
        "steps": [
            "Sit up straight and interlace your fingers in front of you.",
            "Push your hands out in front, rounding your upper back like a gentle hump.",
            "Hold the stretch for 5 seconds, feeling it across your shoulder blades.",
            "Release and sit tall again.",
            "Repeat 3 times. Breathe slowly throughout.",
        ],
    },
    {
        "title": "Seated Hip March",
        "description": "A gentle movement to wake up your hips and legs.",
        "steps": [
            "Sit near the front edge of your chair with your back straight.",
            "Lift your right knee slowly toward your chest, then lower it.",
            "Lift your left knee slowly, then lower it.",
            "Alternate sides — right, left, right, left — for a count of 10.",
            "Move at a pace that feels comfortable for you.",
        ],
    },
    {
        "title": "Gentle Chest Opener",
        "description": "Open up your chest and improve your posture.",
        "steps": [
            "Sit up tall and clasp your hands behind your back.",
            "Gently squeeze your shoulder blades together and lift your chest.",
            "Hold for 5 seconds, then release.",
            "Repeat this 4 times.",
            "You should feel a pleasant stretch across the front of your chest.",
        ],
    },
    {
        "title": "Chin Tuck",
        "description": "A simple posture exercise to reduce neck tension.",
        "steps": [
            "Sit with your back straight and eyes looking forward.",
            "Gently pull your chin straight back — like making a small double chin.",
            "Hold for 3 seconds, then release.",
            "You should feel a stretch at the base of your skull.",
            "Repeat 6 times. This helps with posture and neck comfort.",
        ],
    },
    {
        "title": "Seated Side Bend",
        "description": "A gentle stretch for the sides of your body.",
        "steps": [
            "Sit upright with your feet flat on the floor.",
            "Raise your right arm above your head.",
            "Lean gently to the left, reaching your right arm over.",
            "Hold for 5 seconds, feeling the stretch along your right side.",
            "Return to center and repeat on the other side. Do 3 on each side.",
        ],
    },
    {
        "title": "Deep Breathing Exercise",
        "description": "Calm your mind and body with this slow breathing stretch.",
        "steps": [
            "Sit comfortably with both feet on the floor and your hands on your lap.",
            "Take a slow, deep breath in through your nose for 4 counts.",
            "Hold the breath gently for 2 counts.",
            "Breathe out slowly through your mouth for 6 counts.",
            "Repeat this 5 times and notice how relaxed you feel.",
        ],
    },
    {
        "title": "Seated Torso Twist",
        "description": "Gently rotate your spine to ease stiffness.",
        "steps": [
            "Sit upright with your feet flat on the floor.",
            "Place your left hand on your right knee.",
            "Slowly twist your torso to the right, looking over your right shoulder.",
            "Hold for 5 seconds, then gently return to center.",
            "Repeat on the other side. Do 3 twists on each side.",
        ],
    },
    {
        "title": "Finger Spread & Flex",
        "description": "A lovely warm-up for your hands and fingers.",
        "steps": [
            "Hold one hand up in front of you, palm facing away.",
            "Spread your fingers as wide as you can, holding for 3 seconds.",
            "Bring your fingers together gently and make a relaxed fist.",
            "Hold for 3 seconds, then spread open again.",
            "Repeat 8 times on each hand.",
        ],
    },
    {
        "title": "Ear to Shoulder Neck Rolls",
        "description": "A slow, soothing neck stretch to start the day gently.",
        "steps": [
            "Sit up straight and drop your chin slowly toward your chest.",
            "Gently roll your right ear toward your right shoulder.",
            "Pause when you feel a comfortable stretch — no pain.",
            "Slowly roll back through center and to the left side.",
            "Repeat this slow roll 4 times. Never force it.",
        ],
    },
    {
        "title": "Heel & Toe Lifts",
        "description": "Improve circulation in your feet and calves.",
        "steps": [
            "Sit with feet flat on the floor, hip-width apart.",
            "Raise both heels off the floor, keeping your toes down. Hold 3 seconds.",
            "Lower your heels and raise your toes off the floor instead. Hold 3 seconds.",
            "Alternate heel raises and toe raises 10 times each.",
            "This is excellent for blood flow in your lower legs.",
        ],
    },
    {
        "title": "Cat & Cow Seated Spine",
        "description": "A gentle spinal movement borrowed from yoga, done in your chair.",
        "steps": [
            "Sit on the edge of your chair with feet flat on the floor.",
            "Take a breath in and arch your back gently, lifting your chest and tilting your pelvis forward.",
            "Breathe out and round your back, dropping your chin and tucking your hips under.",
            "Flow back and forth slowly — in is arched, out is rounded.",
            "Repeat 6 times. Move slowly and gently.",
        ],
    },
    {
        "title": "Elbow Circles",
        "description": "Warm up your shoulders and elbows with slow, gentle circles.",
        "steps": [
            "Sit tall and place your fingertips lightly on your shoulders.",
            "Slowly rotate both elbows forward in large circles — 5 times.",
            "Then reverse and circle them backward — 5 times.",
            "Feel the gentle movement through your shoulder joints.",
            "Lower your arms and shake them out softly.",
        ],
    },
    {
        "title": "Seated Knee Extension",
        "description": "Strengthen and loosen the muscles around your knees.",
        "steps": [
            "Sit upright with your feet flat on the floor.",
            "Slowly straighten your right leg until it is nearly parallel with the floor.",
            "Hold for 3 seconds, then gently lower it.",
            "Repeat 8 times on the right leg, then switch to the left.",
            "This is a wonderful exercise for knee health and leg circulation.",
        ],
    },
    {
        "title": "Jaw & Face Relaxation",
        "description": "Release tension held in your face and jaw muscles.",
        "steps": [
            "Sit comfortably and let your shoulders drop.",
            "Open your mouth wide as if yawning, hold for 3 seconds, then close.",
            "Clench your jaw gently, hold for 2 seconds, then completely relax.",
            "Raise your eyebrows high, hold for 2 seconds, then let your face go soft.",
            "Repeat the whole sequence 3 times. Feel the tension melt away.",
        ],
    },
    {
        "title": "Seated Forward Lean",
        "description": "A gentle stretch for your lower back and hamstrings.",
        "steps": [
            "Sit near the front of your chair with feet hip-width apart.",
            "Place your hands on your thighs and take a breath in.",
            "As you breathe out, slowly lean your chest forward toward your knees.",
            "Go only as far as is comfortable — feel the stretch in your lower back.",
            "Hold for 5 seconds, breathe in to sit back up. Repeat 4 times.",
        ],
    },
    {
        "title": "Shoulder Blade Squeeze",
        "description": "Improve your posture by activating the muscles between your shoulder blades.",
        "steps": [
            "Sit up straight and let your arms hang loosely at your sides.",
            "Squeeze your shoulder blades together as if trying to hold a pencil between them.",
            "Hold the squeeze for 5 seconds, then release completely.",
            "Repeat 8 times. Breathe normally throughout.",
            "You should feel this strongly between your shoulder blades.",
        ],
    },
    {
        "title": "Seated Hip Circles",
        "description": "Loosen your hips with this gentle circular movement.",
        "steps": [
            "Sit near the front of your chair with both feet flat on the floor.",
            "Place your hands on your hips and slowly circle your hips to the right — 5 times.",
            "Then circle to the left — 5 times.",
            "Keep your movements slow and controlled.",
            "This is wonderful for lower back and hip flexibility.",
        ],
    },
    {
        "title": "Arm Raise & Lower",
        "description": "Strengthen your shoulders and improve range of motion.",
        "steps": [
            "Sit tall with your arms resting at your sides.",
            "Slowly raise both arms out to the sides and up overhead, if comfortable.",
            "Hold at the top for 3 seconds.",
            "Slowly lower your arms back down to your sides.",
            "Repeat 6 times. Move at a pace that feels easy and gentle.",
        ],
    },
    {
        "title": "Neck Forward & Back",
        "description": "Release tension in the front and back of your neck.",
        "steps": [
            "Sit upright with your eyes looking forward.",
            "Slowly drop your chin toward your chest, feeling a stretch in the back of your neck.",
            "Hold for 5 seconds, then slowly lift your head back to neutral.",
            "Gently tip your head back slightly and look up toward the ceiling.",
            "Hold for 3 seconds, then return to neutral. Repeat 3 times each way.",
        ],
    },
    {
        "title": "Thumb Opposition",
        "description": "A fine motor exercise to keep your fingers nimble.",
        "steps": [
            "Hold your right hand in front of you.",
            "Touch the tip of your thumb to the tip of your index finger to form a circle.",
            "Move to the middle finger, then ring finger, then little finger.",
            "Reverse back from little finger to index finger.",
            "Repeat the sequence 5 times on each hand.",
        ],
    },
    {
        "title": "Seated Calf Raise",
        "description": "Strengthen your calf muscles and boost circulation in your lower legs.",
        "steps": [
            "Sit tall with both feet flat on the floor.",
            "Raise both heels off the floor as high as you comfortably can.",
            "Hold at the top for 2 seconds.",
            "Slowly lower your heels back to the floor.",
            "Repeat 12 times. This is excellent for leg circulation.",
        ],
    },
    {
        "title": "Cross-Body Arm Stretch",
        "description": "Stretch the back of your shoulder and upper arm.",
        "steps": [
            "Sit comfortably and bring your right arm across your chest.",
            "Use your left hand to gently hold the right arm just above the elbow.",
            "Hold the stretch for 10 seconds, feeling it in the back of your shoulder.",
            "Release and repeat on the other side.",
            "Do 3 repetitions on each side.",
        ],
    },
    {
        "title": "Seated March with Arm Swing",
        "description": "A gentle coordination exercise combining legs and arms.",
        "steps": [
            "Sit up straight near the front of your chair.",
            "Lift your right knee as you swing your left arm forward.",
            "Lower the right knee as you lift your left knee and swing your right arm forward.",
            "Continue alternating in a slow, comfortable marching rhythm.",
            "March for a count of 20, then rest and breathe.",
        ],
    },
    {
        "title": "Eyebrow & Forehead Massage",
        "description": "Relieve tension in your forehead with this soothing self-massage.",
        "steps": [
            "Place your fingertips on your forehead just above your eyebrows.",
            "With gentle circular pressure, massage slowly outward toward your temples.",
            "Repeat 5 times.",
            "Then use your thumbs to gently press along the bone just above each eyebrow.",
            "Hold each spot for 2 seconds as you move outward. Repeat twice.",
        ],
    },
    {
        "title": "Prayer Hands Wrist Stretch",
        "description": "A gentle wrist and forearm stretch done with pressed palms.",
        "steps": [
            "Sit comfortably and press your palms together in front of your chest.",
            "Slowly lower your joined hands toward your waist, keeping your palms together.",
            "You should feel a stretch in your wrists and forearms.",
            "Hold for 10 seconds, then raise your hands back up.",
            "Repeat 4 times.",
        ],
    },
    {
        "title": "Seated Tricep Stretch",
        "description": "Stretch the back of your upper arm.",
        "steps": [
            "Sit tall and raise your right arm overhead.",
            "Bend the elbow so your right hand reaches toward your left shoulder blade.",
            "Use your left hand to gently press down on the right elbow.",
            "Hold for 10 seconds, feeling the stretch in the back of your arm.",
            "Switch sides and repeat. Do 3 on each side.",
        ],
    },
    {
        "title": "Spinal Roll-Down",
        "description": "A slow roll through the spine to ease stiffness.",
        "steps": [
            "Sit near the front of your chair with feet hip-width apart.",
            "Drop your chin to your chest and slowly curl forward, vertebra by vertebra.",
            "Let your arms hang down loosely toward the floor.",
            "Breathe out as you round down. Hold for 5 seconds.",
            "Breathe in and slowly uncurl back to sitting tall.",
        ],
    },
    {
        "title": "Leg Tap & Point",
        "description": "Activate your lower leg muscles with this simple movement.",
        "steps": [
            "Sit tall with feet flat on the floor.",
            "Tap your right heel on the floor twice, then point your right toes up twice.",
            "Repeat with your left foot.",
            "Continue alternating — heel-tap, toe-point — for a count of 20.",
            "This wakes up your ankles and lower legs gently.",
        ],
    },
    {
        "title": "Seated Chest Squeeze",
        "description": "Activate your chest and arms with this isometric exercise.",
        "steps": [
            "Sit tall and bring your hands together in front of your chest.",
            "Press your palms firmly against each other.",
            "Hold the squeeze for 5 seconds — you should feel your chest and arms engage.",
            "Slowly release.",
            "Repeat 8 times. Breathe normally throughout.",
        ],
    },
    {
        "title": "Sky Reach",
        "description": "Lengthen your whole body with this upward arm stretch.",
        "steps": [
            "Sit tall and reach both arms up toward the ceiling.",
            "Reach your right hand a little higher, stretching up through your waist.",
            "Then reach your left hand a little higher.",
            "Alternate 5 times on each side.",
            "Lower your arms slowly and take a deep breath.",
        ],
    },
    {
        "title": "Side-to-Side Head Turn",
        "description": "Improve neck mobility and awareness.",
        "steps": [
            "Sit up straight with your chin level.",
            "Slowly turn your head to look over your right shoulder as far as is comfortable.",
            "Hold for 3 seconds.",
            "Slowly return to center, then turn to look over your left shoulder.",
            "Hold for 3 seconds. Repeat 5 times each side. Move slowly and gently.",
        ],
    },
    {
        "title": "Seated Spinal Elongation",
        "description": "Improve posture and decompress your spine.",
        "steps": [
            "Sit comfortably and place your feet flat on the floor.",
            "Imagine a string gently pulling the top of your head upward toward the ceiling.",
            "Slowly grow as tall as you can in your chair.",
            "Hold this tall posture for 10 seconds, breathing normally.",
            "Release and relax. Repeat 5 times.",
        ],
    },
    {
        "title": "Fist Squeeze & Release",
        "description": "Strengthen your grip and improve hand circulation.",
        "steps": [
            "Hold both hands out in front of you.",
            "Squeeze your fingers into tight fists as firmly as you comfortably can.",
            "Hold for 5 seconds, then open your hands wide.",
            "Repeat 10 times.",
            "Finish by gently shaking your hands out.",
        ],
    },
    {
        "title": "Seated Lunge Stretch",
        "description": "A gentle hip flexor stretch adapted for the chair.",
        "steps": [
            "Sit sideways on the front half of your chair, left leg dangling off the side.",
            "Slowly slide your left foot back as far as feels comfortable.",
            "Keep your back straight and feel a gentle stretch in the front of your left hip.",
            "Hold for 10 seconds, then return to sitting straight.",
            "Turn to the other side and repeat with your right leg.",
        ],
    },
    {
        "title": "Scalp Massage",
        "description": "A soothing self-massage to ease tension and improve relaxation.",
        "steps": [
            "Place your fingertips on the top of your head.",
            "Using gentle circular movements, massage slowly across your scalp.",
            "Work from the top of your head toward the back and sides.",
            "Spend about 30 seconds massaging, enjoying the sensation.",
            "Finish with a slow, deep breath and feel how relaxed your head and neck feel.",
        ],
    },
    {
        "title": "Abdominal Breath",
        "description": "Learn belly breathing to fully relax and oxygenate your body.",
        "steps": [
            "Sit with one hand on your chest and one hand on your belly.",
            "Breathe in slowly, trying to push your belly hand outward while keeping your chest hand still.",
            "Breathe out and let your belly hand fall back in.",
            "This is called diaphragm breathing and is very calming.",
            "Practice 8 belly breaths. Feel yourself relax with each breath out.",
        ],
    },
    {
        "title": "Seated Inner Thigh Squeeze",
        "description": "Gently activate the inner thigh muscles from your chair.",
        "steps": [
            "Sit tall and place a cushion or folded towel between your knees.",
            "Slowly squeeze your knees together against the cushion.",
            "Hold for 5 seconds, then release.",
            "Repeat 10 times.",
            "If you don't have a cushion, simply press your knees together gently.",
        ],
    },
    {
        "title": "Neck Half-Circles",
        "description": "A gentle rolling stretch for the front and sides of the neck.",
        "steps": [
            "Sit upright and drop your chin slowly to your chest.",
            "Gently roll your head to the right, right ear toward right shoulder.",
            "Roll back through center to the left side.",
            "Only roll the front half — do not roll your head backward.",
            "Do 5 gentle half-circles in each direction. Move slowly.",
        ],
    },
    {
        "title": "Shoulder Shrug & Drop",
        "description": "Release built-up tension in your neck and shoulders.",
        "steps": [
            "Sit tall and take a slow breath in.",
            "Raise both shoulders up toward your ears as high as they will go.",
            "Hold for 3 seconds.",
            "Then drop them down suddenly and completely, letting all the tension go.",
            "Repeat 6 times. Feel the release each time you drop your shoulders.",
        ],
    },
    {
        "title": "Tummy Tuck",
        "description": "Gently activate your core muscles from a seated position.",
        "steps": [
            "Sit near the front of your chair with feet flat on the floor.",
            "Take a breath in to prepare.",
            "As you breathe out, gently pull your belly button in toward your spine.",
            "Hold this gentle tummy tuck for 5 seconds while continuing to breathe.",
            "Relax and repeat 10 times. This helps support your back.",
        ],
    },
    {
        "title": "Chair-Supported Standing",
        "description": "Practice the sit-to-stand movement to build leg strength and confidence.",
        "steps": [
            "Sit near the front of your chair, feet hip-width apart.",
            "Lean slightly forward and slowly rise to a standing position.",
            "Hold for 3 seconds, gripping the chair arms if needed.",
            "Slowly lower yourself back down to sitting.",
            "Repeat 5 times. This is one of the most important exercises for independence.",
        ],
    },
    {
        "title": "Seated Butterfly",
        "description": "Open your hips and inner thighs with this classic stretch.",
        "steps": [
            "Sit toward the front of your chair.",
            "Place the soles of your feet together, letting your knees fall outward.",
            "Hold your feet and gently press your knees toward the floor.",
            "Hold for 10 seconds, feeling the stretch in your inner thighs.",
            "Release and repeat 4 times.",
        ],
    },
    {
        "title": "Spinal Twist with Chair Back",
        "description": "Use your chair back to deepen a gentle spinal rotation.",
        "steps": [
            "Sit sideways on your chair facing right, with the chair back to your left.",
            "Hold the top of the chair back with both hands.",
            "Use your arms to gently pull yourself into a twist to the left.",
            "Hold for 10 seconds, then face the opposite direction and repeat.",
            "This is a beautiful stretch for the entire length of your spine.",
        ],
    },
    {
        "title": "Wrist Flexion & Extension",
        "description": "Maintain full wrist mobility with these simple movements.",
        "steps": [
            "Hold one arm out in front of you, palm facing down.",
            "Slowly bend your wrist downward, pointing your fingers toward the floor.",
            "Hold for 5 seconds, then bend your wrist upward, fingers toward the ceiling.",
            "Hold for 5 seconds.",
            "Repeat 5 times on each hand.",
        ],
    },
    {
        "title": "Seated Figure-Four Stretch",
        "description": "A gentle hip and piriformis stretch done in the chair.",
        "steps": [
            "Sit tall and cross your right ankle over your left knee.",
            "Keep your right foot flexed to protect the knee.",
            "Gently press down on your right knee with your hand.",
            "Lean forward slightly until you feel a stretch deep in your right hip.",
            "Hold for 15 seconds, then switch sides. Repeat 3 times each.",
        ],
    },
    {
        "title": "Seated Lat Stretch",
        "description": "Stretch the large muscles running down the sides of your back.",
        "steps": [
            "Sit tall and raise your right arm directly overhead.",
            "Grasp your right wrist with your left hand.",
            "Gently pull your right arm to the left, leaning your body with it.",
            "Hold for 10 seconds, feeling the stretch down your right side.",
            "Switch sides. Repeat 3 times on each side.",
        ],
    },
    {
        "title": "Ear Massage",
        "description": "An ancient relaxation technique — massaging your ears releases tension.",
        "steps": [
            "Sit comfortably with your eyes closed.",
            "Use your thumbs and index fingers to gently massage your earlobes.",
            "Work slowly up the outer rim of your ear to the top.",
            "Spend about 30 seconds on each ear.",
            "Many people find this surprisingly relaxing and calming.",
        ],
    },
    {
        "title": "Seated Wing Stretch",
        "description": "Open your chest and stretch your arms like bird wings.",
        "steps": [
            "Sit tall and extend both arms out to the sides at shoulder height.",
            "Turn your palms upward and gently squeeze your shoulder blades together.",
            "Hold for 5 seconds, feeling your chest open.",
            "Lower your arms, then repeat.",
            "Do this 6 times. Breathe in when you open, out when you lower.",
        ],
    },
    {
        "title": "Toe Curls & Spreads",
        "description": "Improve foot mobility and circulation with this toe exercise.",
        "steps": [
            "Sit with shoes off if possible, feet flat on the floor.",
            "Curl all your toes tightly downward. Hold for 3 seconds.",
            "Spread all your toes as wide apart as you can. Hold for 3 seconds.",
            "Alternate between curling and spreading 10 times.",
            "Your feet will feel wonderfully refreshed.",
        ],
    },
    {
        "title": "Neck & Shoulder Combined Stretch",
        "description": "A two-in-one stretch for neck and shoulder relief.",
        "steps": [
            "Sit tall and reach your right arm down behind the right side of your chair back.",
            "Gently tilt your left ear toward your left shoulder at the same time.",
            "You will feel a strong stretch from your right neck down into your shoulder.",
            "Hold for 10 seconds, then release.",
            "Repeat on the other side. Do 3 on each side.",
        ],
    },
    {
        "title": "Seated Spinal Wave",
        "description": "A flowing movement that warms up your entire spine.",
        "steps": [
            "Sit tall near the front of your chair.",
            "Start by tilting your pelvis forward, then let the movement flow up through your lower back, middle back, and up to your head.",
            "Now reverse — drop your head, then round your upper back, then middle back, then tuck your pelvis under.",
            "Flow slowly up and down like a gentle wave.",
            "Repeat 5 times. Let your breath guide the movement.",
        ],
    },
    {
        "title": "Hand Clasp Overhead Stretch",
        "description": "Stretch both arms and sides at the same time.",
        "steps": [
            "Sit tall and interlace your fingers in front of you.",
            "Turn your palms outward and slowly raise your clasped hands overhead.",
            "Stretch gently up toward the ceiling.",
            "Hold for 10 seconds, breathing comfortably.",
            "Lower your arms slowly. Repeat 4 times.",
        ],
    },
    {
        "title": "Seated Pigeon Pose",
        "description": "A gentle hip-opening stretch using your chair for support.",
        "steps": [
            "Sit toward the front of your chair.",
            "Lift your right foot and place it gently on top of your left knee.",
            "Sit tall and lean gently forward from your hips — not your waist.",
            "Hold for 15–20 seconds, feeling the stretch deep in your right hip.",
            "Switch legs. Repeat 3 times on each side.",
        ],
    },
    {
        "title": "Eye Exercise",
        "description": "Rest and refresh tired eyes with this gentle movement.",
        "steps": [
            "Sit comfortably and keep your head still throughout.",
            "Look up as far as you can, then down. Repeat 5 times.",
            "Look as far to the right as you can, then to the left. Repeat 5 times.",
            "Make slow, large circles with your eyes — 5 times each direction.",
            "Finish by closing your eyes tightly, then opening them wide. Repeat 3 times.",
        ],
    },
    {
        "title": "Seated Side Leg Lift",
        "description": "Strengthen your outer hip muscles from a seated position.",
        "steps": [
            "Sit near the edge of your chair with feet together on the floor.",
            "Slowly slide your right foot out to the side, lifting it slightly.",
            "Hold for 2 seconds, then slide it back.",
            "Repeat 10 times on the right, then 10 times on the left.",
            "This helps strengthen the muscles around your hips.",
        ],
    },
    {
        "title": "Neck Self-Massage",
        "description": "Relieve neck tension with your own hands.",
        "steps": [
            "Sit comfortably and reach your right hand to the back of your neck.",
            "Gently squeeze and knead the muscles on the right side of your neck.",
            "Work from the base of the skull down to the top of your shoulder.",
            "Spend about 30 seconds on the right side, then switch to the left.",
            "Feel the tension releasing as you work.",
        ],
    },
    {
        "title": "Seated Twisting Knee Lift",
        "description": "Combine a trunk twist and knee lift for a full-body wake-up.",
        "steps": [
            "Sit near the front of your chair, hands behind your head.",
            "As you lift your right knee, twist your upper body gently to the right.",
            "Lower the knee and return to center.",
            "Lift your left knee and twist to the left.",
            "Alternate sides for a count of 10 (5 each side). Move slowly.",
        ],
    },
    {
        "title": "Resisted Arm Press",
        "description": "Build gentle upper body strength without any equipment.",
        "steps": [
            "Sit tall and place your right palm on your right thigh.",
            "Push your palm downward against your thigh while resisting with your leg.",
            "Hold this isometric squeeze for 5 seconds.",
            "Release and repeat on the left side.",
            "Do 6 repetitions on each side.",
        ],
    },
    {
        "title": "Seated Spinal Side Lean with Breath",
        "description": "Combine movement and breathing for a calming stretch.",
        "steps": [
            "Sit tall with your hands resting on your thighs.",
            "Take a slow breath in, then as you breathe out, lean gently to the right.",
            "Breathe in to return to center.",
            "Breathe out and lean gently to the left.",
            "Continue this breathing side-bend for 6 full breaths. Very calming.",
        ],
    },
    {
        "title": "Chair-Back Shoulder Opener",
        "description": "Use your chair back to open up tight chest and shoulders.",
        "steps": [
            "Sit facing away from your chair back, close to the edge.",
            "Reach both arms back and grip the top of the chair back.",
            "Gently push your chest forward and upward, lifting your chin.",
            "Hold for 10 seconds, feeling an opening across your chest.",
            "Release, rest, and repeat 3 times.",
        ],
    },
    {
        "title": "Alternate Shoulder Press",
        "description": "Lift and lower each shoulder independently to release asymmetric tension.",
        "steps": [
            "Sit tall with arms relaxed at your sides.",
            "Lift your right shoulder up toward your ear, hold for 3 seconds, then drop it.",
            "Lift your left shoulder up toward your ear, hold for 3 seconds, then drop it.",
            "Alternate for 8 repetitions each side.",
            "Notice if one side feels tighter — it probably does!",
        ],
    },
    {
        "title": "Foot Rolling",
        "description": "Massage the soles of your feet for relaxation and comfort.",
        "steps": [
            "Remove your shoes and sit comfortably.",
            "Place a tennis ball or water bottle under your right foot.",
            "Gently roll it back and forth under your foot for 30 seconds.",
            "Pay extra attention to any areas that feel tender.",
            "Switch to the left foot. Your feet will feel wonderful afterward.",
        ],
    },
    {
        "title": "Pursed Lip Breathing",
        "description": "A breathing technique that slows your breath and promotes calm.",
        "steps": [
            "Sit comfortably with your shoulders relaxed.",
            "Breathe in slowly through your nose for 2 counts.",
            "Pucker your lips as if you were going to whistle.",
            "Breathe out slowly through pursed lips for 4 counts.",
            "Repeat 8 times. This technique is excellent for calming the nervous system.",
        ],
    },
    {
        "title": "Neck Isometric Press",
        "description": "Strengthen your neck muscles gently without movement.",
        "steps": [
            "Sit tall and place your right palm against the right side of your head.",
            "Press your head gently into your hand while resisting with your hand — do not move.",
            "Hold this isometric contraction for 5 seconds, then release.",
            "Repeat on the left side, then front and back.",
            "Do 3 repetitions on each side. Your neck will feel stronger and more supported.",
        ],
    },
    {
        "title": "Seated Hip Abduction",
        "description": "Work the outer hip and thigh muscles from your chair.",
        "steps": [
            "Sit near the edge of your chair, feet together on the floor.",
            "Place your hands on the outside of your thighs just above the knees.",
            "Try to push your knees apart while resisting with your hands.",
            "Hold the push for 5 seconds, then release.",
            "Repeat 10 times. This strengthens the outer hip muscles.",
        ],
    },
    {
        "title": "Good Morning Stretch",
        "description": "A full-body seated wake-up to start the day feeling wonderful.",
        "steps": [
            "Sit tall with your feet flat on the floor.",
            "Interlace your fingers and stretch your arms overhead with palms facing up.",
            "Take a slow, deep breath in and reach up as far as is comfortable.",
            "Breathe out and lower your arms to shoulder height.",
            "Repeat the reach-and-lower 5 times, then sit quietly for a moment.",
        ],
    },
]


class MorningStretchProvider(BaseCareCircleProvider):
    provider_key = "morning_stretch"
    is_safe_for_patient = True

    """
    Delivers a gentle seated stretching exercise from a large curated pool.
    Pure static provider — no external calls required.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pool = cfg.get("stretches", STRETCHES)
        stretch = random.choice(pool)
        return {
            "title": stretch["title"],
            "description": stretch["description"],
            "steps": stretch["steps"],
        }
