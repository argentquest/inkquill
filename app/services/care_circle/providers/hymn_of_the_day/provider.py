"""
Hymn of the Day provider for Care Circle patient sessions.
Delivers a beloved hymn or classic spiritual song with a short lyrics excerpt.
Static provider — no LLM or external calls required.
"""

import random
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


HYMNS = [
    {
        "title": "Amazing Grace",
        "era": "1779",
        "note": "Written by John Newton, this beloved hymn is one of the most recognizable songs in the English-speaking world.",
        "lyrics_excerpt": (
            "Amazing grace! How sweet the sound\n"
            "That saved a wretch like me!\n"
            "I once was lost, but now am found;\n"
            "Was blind, but now I see."
        ),
    },
    {
        "title": "How Great Thou Art",
        "era": "1885",
        "note": "Originally a Swedish poem, this hymn became one of the best-loved worship songs of the 20th century.",
        "lyrics_excerpt": (
            "O Lord my God, when I in awesome wonder\n"
            "Consider all the worlds Thy hands have made,\n"
            "I see the stars, I hear the rolling thunder,\n"
            "Thy power throughout the universe displayed."
        ),
    },
    {
        "title": "What a Friend We Have in Jesus",
        "era": "1855",
        "note": "Written by Joseph Scriven as a poem of comfort, this hymn has brought peace to countless generations.",
        "lyrics_excerpt": (
            "What a friend we have in Jesus,\n"
            "All our sins and griefs to bear!\n"
            "What a privilege to carry\n"
            "Everything to God in prayer!"
        ),
    },
    {
        "title": "Rock of Ages",
        "era": "1775",
        "note": "Written by Augustus Toplady, this classic hymn of refuge has been sung for over 200 years.",
        "lyrics_excerpt": (
            "Rock of Ages, cleft for me,\n"
            "Let me hide myself in Thee;\n"
            "Let the water and the blood,\n"
            "From Thy riven side which flowed."
        ),
    },
    {
        "title": "Great Is Thy Faithfulness",
        "era": "1923",
        "note": "Inspired by Lamentations 3:23, this hymn by Thomas Chisholm celebrates God's unwavering faithfulness.",
        "lyrics_excerpt": (
            "Great is Thy faithfulness, O God my Father;\n"
            "There is no shadow of turning with Thee;\n"
            "Thou changest not, Thy compassions, they fail not;\n"
            "As Thou hast been, Thou forever wilt be."
        ),
    },
    {
        "title": "In the Garden",
        "era": "1912",
        "note": "Written by C. Austin Miles, this tender hymn speaks of a quiet, personal walk with God.",
        "lyrics_excerpt": (
            "I come to the garden alone,\n"
            "While the dew is still on the roses;\n"
            "And the voice I hear, falling on my ear,\n"
            "The Son of God discloses."
        ),
    },
    {
        "title": "It Is Well with My Soul",
        "era": "1873",
        "note": "Written by Horatio Spafford after great tragedy, this hymn is a powerful statement of peace and faith.",
        "lyrics_excerpt": (
            "When peace like a river attendeth my way,\n"
            "When sorrows like sea billows roll;\n"
            "Whatever my lot, Thou hast taught me to say,\n"
            "It is well, it is well with my soul."
        ),
    },
    {
        "title": "Blessed Assurance",
        "era": "1873",
        "note": "Written by Fanny Crosby, one of the most prolific hymn writers in history, despite being blind from infancy.",
        "lyrics_excerpt": (
            "Blessed assurance, Jesus is mine!\n"
            "Oh, what a foretaste of glory divine!\n"
            "Heir of salvation, purchase of God,\n"
            "Born of His Spirit, washed in His blood."
        ),
    },
    {
        "title": "Abide with Me",
        "era": "1847",
        "note": "Written by Henry Lyte as he faced his own death, this hymn is a comforting prayer for God's presence.",
        "lyrics_excerpt": (
            "Abide with me; fast falls the eventide;\n"
            "The darkness deepens; Lord, with me abide;\n"
            "When other helpers fail and comforts flee,\n"
            "Help of the helpless, oh, abide with me."
        ),
    },
    {
        "title": "The Old Rugged Cross",
        "era": "1912",
        "note": "Written by George Bennard, this hymn became one of the most beloved gospel songs of the 20th century.",
        "lyrics_excerpt": (
            "On a hill far away stood an old rugged cross,\n"
            "The emblem of suffering and shame;\n"
            "And I love that old cross where the dearest and best\n"
            "For a world of lost sinners was slain."
        ),
    },
    {
        "title": "How Firm a Foundation",
        "era": "1787",
        "note": "An old hymn of endurance and strength, built on the promises of Scripture for all of life's trials.",
        "lyrics_excerpt": (
            "How firm a foundation, ye saints of the Lord,\n"
            "Is laid for your faith in His excellent word!\n"
            "What more can He say than to you He hath said,\n"
            "To you who for refuge to Jesus have fled?"
        ),
    },
    {
        "title": "Be Thou My Vision",
        "era": "6th Century",
        "note": "An ancient Irish hymn translated into English in 1905, it is a beautiful prayer for divine guidance.",
        "lyrics_excerpt": (
            "Be Thou my vision, O Lord of my heart;\n"
            "Naught be all else to me, save that Thou art;\n"
            "Thou my best thought by day or by night,\n"
            "Waking or sleeping, Thy presence my light."
        ),
    },
    {
        "title": "To God Be the Glory",
        "era": "1875",
        "note": "Written by Fanny Crosby and popularised by Billy Graham's crusades, this joyful hymn is loved worldwide.",
        "lyrics_excerpt": (
            "To God be the glory, great things He hath taught us,\n"
            "Great things He hath done, and great our rejoicing;\n"
            "Through Jesus the Son who yielded His life\n"
            "An earnest desire to fill the skies."
        ),
    },
    {
        "title": "Fairest Lord Jesus",
        "era": "1677",
        "note": "A German hymn of adoration, this song praises the beauty of Jesus found in creation and in faith.",
        "lyrics_excerpt": (
            "Fairest Lord Jesus, ruler of all nature,\n"
            "O Thou of God and man the Son;\n"
            "Thee will I cherish, Thee will I honor,\n"
            "Thou, my soul's glory, joy, and crown."
        ),
    },
    {
        "title": "I Need Thee Every Hour",
        "era": "1872",
        "note": "Annie Hawks wrote this hymn while doing housework — a simple, heartfelt prayer of daily dependence.",
        "lyrics_excerpt": (
            "I need Thee every hour, most gracious Lord;\n"
            "No tender voice like Thine can peace afford.\n"
            "I need Thee, oh, I need Thee;\n"
            "Every hour I need Thee!"
        ),
    },
    {
        "title": "His Eye Is on the Sparrow",
        "era": "1905",
        "note": "Written by Civilla Martin, inspired by a bedridden friend who said, 'His eye is on the sparrow — so I know He watches me.'",
        "lyrics_excerpt": (
            "Why should I feel discouraged?\n"
            "Why should the shadows come?\n"
            "Why should my heart be lonely\n"
            "And long for heaven and home?"
        ),
    },
    {
        "title": "Trust and Obey",
        "era": "1887",
        "note": "Written by John Sammis after hearing a young man testify about trusting God — its simple message still resonates today.",
        "lyrics_excerpt": (
            "When we walk with the Lord in the light of His word,\n"
            "What a glory He sheds on our way!\n"
            "While we do His good will, He abides with us still,\n"
            "And with all who will trust and obey."
        ),
    },
    {
        "title": "Standing on the Promises",
        "era": "1886",
        "note": "R. Kelso Carter wrote this triumphant hymn using musical imagery of standing firm on the Word of God.",
        "lyrics_excerpt": (
            "Standing on the promises of Christ my King,\n"
            "Through eternal ages let His praises ring;\n"
            "Glory in the highest, I will shout and sing,\n"
            "Standing on the promises of God."
        ),
    },
    {
        "title": "Sweet Hour of Prayer",
        "era": "1845",
        "note": "Written by William Walford, a blind preacher who dictated the poem from memory, this hymn is a serene reflection on prayer.",
        "lyrics_excerpt": (
            "Sweet hour of prayer! Sweet hour of prayer!\n"
            "That calls me from a world of care,\n"
            "And bids me at my Father's throne\n"
            "Make all my wants and wishes known."
        ),
    },
    {
        "title": "Leaning on the Everlasting Arms",
        "era": "1887",
        "note": "Inspired by Deuteronomy 33:27, this joyful song of security was written by Elisha Hoffman.",
        "lyrics_excerpt": (
            "What a fellowship, what a joy divine,\n"
            "Leaning on the everlasting arms;\n"
            "What a blessedness, what a peace is mine,\n"
            "Leaning on the everlasting arms."
        ),
    },
    # — second 20 —
    {
        "title": "O How I Love Jesus",
        "era": "1855",
        "note": "Based on a poem by Frederick Whitfield, this simple declaration of love for Jesus remains a favourite in congregations worldwide.",
        "lyrics_excerpt": (
            "There is a name I love to hear,\n"
            "I love to sing its worth;\n"
            "It sounds like music in mine ear,\n"
            "The sweetest name on earth."
        ),
    },
    {
        "title": "Just a Closer Walk with Thee",
        "era": "Early 1900s",
        "note": "A beloved Southern gospel hymn whose exact origin is unknown, cherished for its simple prayer for closeness with God.",
        "lyrics_excerpt": (
            "Just a closer walk with Thee,\n"
            "Grant it, Jesus, is my plea;\n"
            "Daily walking close to Thee,\n"
            "Let it be, dear Lord, let it be."
        ),
    },
    {
        "title": "Victory in Jesus",
        "era": "1939",
        "note": "Written by E.M. Bartlett near the end of his life, this triumphant hymn quickly became one of the most loved gospel songs of the 20th century.",
        "lyrics_excerpt": (
            "O victory in Jesus,\n"
            "My Savior forever!\n"
            "He sought me and bought me\n"
            "With His redeeming blood."
        ),
    },
    {
        "title": "Softly and Tenderly",
        "era": "1880",
        "note": "Written by Will Thompson on his deathbed, this gentle invitation hymn moved Dwight L. Moody so deeply he wished he had written it himself.",
        "lyrics_excerpt": (
            "Softly and tenderly Jesus is calling,\n"
            "Calling for you and for me;\n"
            "See, on the portals He's waiting and watching,\n"
            "Watching for you and for me."
        ),
    },
    {
        "title": "Shall We Gather at the River",
        "era": "1864",
        "note": "Robert Lowry wrote this hymn during a devastating heat wave, finding comfort in the image of heaven's river of life.",
        "lyrics_excerpt": (
            "Shall we gather at the river,\n"
            "Where bright angel feet have trod,\n"
            "With its crystal tide forever\n"
            "Flowing by the throne of God?"
        ),
    },
    {
        "title": "Pass Me Not, O Gentle Savior",
        "era": "1868",
        "note": "Fanny Crosby wrote this heartfelt plea after hearing a prisoner cry out the words that inspired the chorus.",
        "lyrics_excerpt": (
            "Pass me not, O gentle Savior,\n"
            "Hear my humble cry;\n"
            "While on others Thou art calling,\n"
            "Do not pass me by."
        ),
    },
    {
        "title": "O Worship the King",
        "era": "1833",
        "note": "Written by Sir Robert Grant and based on Psalm 104, this majestic hymn of praise has been sung in churches for nearly 200 years.",
        "lyrics_excerpt": (
            "O worship the King all-glorious above,\n"
            "O gratefully sing His power and His love;\n"
            "Our Shield and Defender, the Ancient of Days,\n"
            "Pavilioned in splendour and girded with praise."
        ),
    },
    {
        "title": "Wonderful Grace of Jesus",
        "era": "1918",
        "note": "Haldor Lillenas wrote this jubilant hymn while working as a minister, celebrating the boundless grace of God.",
        "lyrics_excerpt": (
            "Wonderful grace of Jesus,\n"
            "Greater than all my sin;\n"
            "How shall my tongue describe it,\n"
            "Where shall its praise begin?"
        ),
    },
    {
        "title": "All Creatures of Our God and King",
        "era": "1225",
        "note": "Based on a canticle written by Francis of Assisi in 1225, this ancient hymn of creation praise remains as loved as ever.",
        "lyrics_excerpt": (
            "All creatures of our God and King,\n"
            "Lift up your voice and with us sing,\n"
            "Alleluia! Alleluia!\n"
            "Thou burning sun with golden beam,\n"
            "Thou silver moon with softer gleam."
        ),
    },
    {
        "title": "This Is My Father's World",
        "era": "1901",
        "note": "Maltbie Babcock wrote this poem while walking to enjoy the beauty of nature — it became a beloved nature hymn.",
        "lyrics_excerpt": (
            "This is my Father's world,\n"
            "And to my listening ears\n"
            "All nature sings, and round me rings\n"
            "The music of the spheres."
        ),
    },
    {
        "title": "Come Thou Fount of Every Blessing",
        "era": "1758",
        "note": "Robert Robinson wrote this hymn at age 22 and it remains a favourite for its poetic beauty and heartfelt devotion.",
        "lyrics_excerpt": (
            "Come, Thou Fount of every blessing,\n"
            "Tune my heart to sing Thy grace;\n"
            "Streams of mercy, never ceasing,\n"
            "Call for songs of loudest praise."
        ),
    },
    {
        "title": "How Can I Keep from Singing",
        "era": "1868",
        "note": "Attributed to Robert Wadsworth Lowry, this serene hymn of joy speaks of a peace that no earthly storm can silence.",
        "lyrics_excerpt": (
            "My life flows on in endless song\n"
            "Above earth's lamentation;\n"
            "I hear the real though far-off hymn\n"
            "That hails a new creation."
        ),
    },
    {
        "title": "Blessed Be the Name",
        "era": "1899",
        "note": "Based on an earlier hymn by Ralph Hudson, this joyful chorus of praise has been sung enthusiastically for over a century.",
        "lyrics_excerpt": (
            "Blessed be the name, blessed be the name,\n"
            "Blessed be the name of the Lord;\n"
            "Blessed be the name, blessed be the name,\n"
            "Blessed be the name of the Lord."
        ),
    },
    {
        "title": "Nearer, My God, to Thee",
        "era": "1841",
        "note": "Written by Sarah Flower Adams, this hymn of spiritual longing is said to have been played by the band on the Titanic as it sank.",
        "lyrics_excerpt": (
            "Nearer, my God, to Thee,\n"
            "Nearer to Thee!\n"
            "E'en though it be a cross\n"
            "That raiseth me."
        ),
    },
    {
        "title": "Turn Your Eyes upon Jesus",
        "era": "1922",
        "note": "Helen Lemmel wrote this hymn after reading a gospel tract, capturing the transforming power of fixing one's gaze on Christ.",
        "lyrics_excerpt": (
            "Turn your eyes upon Jesus,\n"
            "Look full in His wonderful face,\n"
            "And the things of earth will grow strangely dim\n"
            "In the light of His glory and grace."
        ),
    },
    {
        "title": "Revive Us Again",
        "era": "1863",
        "note": "William Mackay wrote this rousing hymn of spiritual renewal. Its chorus — 'Hallelujah! Thine the glory' — remains one of the most sung in history.",
        "lyrics_excerpt": (
            "We praise Thee, O God,\n"
            "For the Son of Thy love,\n"
            "For Jesus who died\n"
            "And is now gone above."
        ),
    },
    {
        "title": "Love Lifted Me",
        "era": "1912",
        "note": "James Rowe wrote this simple but beloved gospel song about being rescued from the storms of life by God's love.",
        "lyrics_excerpt": (
            "I was sinking deep in sin,\n"
            "Far from the peaceful shore,\n"
            "Very deeply stained within,\n"
            "Sinking to rise no more."
        ),
    },
    {
        "title": "Count Your Blessings",
        "era": "1897",
        "note": "Johnson Oatman Jr. wrote this practical, uplifting hymn reminding singers to name their blessings one by one.",
        "lyrics_excerpt": (
            "Count your blessings, name them one by one;\n"
            "Count your blessings, see what God hath done;\n"
            "Count your blessings, name them one by one,\n"
            "And it will surprise you what the Lord hath done."
        ),
    },
    {
        "title": "Higher Ground",
        "era": "1898",
        "note": "Johnson Oatman Jr. also wrote this hymn of spiritual aspiration — longing to rise closer to God with every passing day.",
        "lyrics_excerpt": (
            "I'm pressing on the upward way,\n"
            "New heights I'm gaining every day;\n"
            "Still praying as I'm onward bound,\n"
            "Lord, plant my feet on higher ground."
        ),
    },
    {
        "title": "Footsteps of Jesus",
        "era": "1871",
        "note": "Written by Mary Slade with music by A.B. Everett, this tender hymn invites believers to follow Christ's example step by step.",
        "lyrics_excerpt": (
            "Sweetly, Lord, have we heard Thee calling,\n"
            "Come, follow Me!\n"
            "And we see where Thy footprints falling\n"
            "Lead us to Thee."
        ),
    },
]


class HymnOfTheDayProvider(BaseCareCircleProvider):
    provider_key = "hymn_of_the_day"
    is_safe_for_patient = True

    """
    Delivers a beloved hymn with a short lyrics excerpt and historical note.
    Pure static provider — 20 classic hymns in the curated pool.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pool = cfg.get("hymns", HYMNS)
        entry = random.choice(pool)
        return {
            "title": entry["title"],
            "era": entry["era"],
            "note": entry["note"],
            "lyrics_excerpt": entry["lyrics_excerpt"],
        }
