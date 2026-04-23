"""
Famous Face provider for Care Circle patient sessions.
Delivers a familiar person from history, entertainment, or sport with a fun fact.
Static provider — no LLM or external calls required.
"""

import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.variety_utils import date_seeded_choice

logger = logging.getLogger(__name__)


FAMOUS_FACES = [
    # Entertainment / Music
    {"name": "Frank Sinatra", "era": "1940s–1990s", "category": "Music", "known_for": "Legendary singer and actor, 'The Voice'", "fun_fact": "Frank Sinatra recorded over 1,400 songs in his lifetime, including classics like 'New York, New York' and 'My Way'."},
    {"name": "Doris Day", "era": "1940s–1980s", "category": "Film & Music", "known_for": "Beloved actress and singer of the Golden Hollywood era", "fun_fact": "Doris Day was a passionate animal rights activist and founded the Doris Day Animal Foundation in 1978."},
    {"name": "Elvis Presley", "era": "1950s–1970s", "category": "Music", "known_for": "The King of Rock and Roll", "fun_fact": "Elvis never performed outside the United States or Canada, yet he sold over one billion records worldwide."},
    {"name": "Judy Garland", "era": "1930s–1960s", "category": "Film & Music", "known_for": "Star of The Wizard of Oz and much-loved actress and singer", "fun_fact": "Judy Garland performed 'Over the Rainbow' so movingly that it was later voted the greatest song of the 20th century."},
    {"name": "Dean Martin", "era": "1940s–1980s", "category": "Music & Film", "known_for": "Rat Pack member, singer, actor, and comedian", "fun_fact": "Dean Martin was born Dino Paul Crocetti in Ohio, and learned to speak English as a second language — his first was Italian!"},
    {"name": "Audrey Hepburn", "era": "1950s–1990s", "category": "Film", "known_for": "Iconic actress and humanitarian, star of Breakfast at Tiffany's", "fun_fact": "After retiring from acting, Audrey Hepburn dedicated most of her time to UNICEF, visiting children in need around the world."},
    {"name": "Bob Hope", "era": "1930s–1990s", "category": "Comedy & Entertainment", "known_for": "Comedian who entertained millions of troops abroad", "fun_fact": "Bob Hope performed for American troops for over 50 years, from World War II through to the Gulf War — a record no one has matched."},
    {"name": "Bing Crosby", "era": "1920s–1970s", "category": "Music & Film", "known_for": "Crooner who recorded 'White Christmas', the best-selling single of all time", "fun_fact": "'White Christmas' by Bing Crosby is still the best-selling physical single in history, with over 50 million copies sold."},
    {"name": "Nat King Cole", "era": "1940s–1960s", "category": "Music", "known_for": "Silky-voiced jazz singer and pianist", "fun_fact": "Nat King Cole started as a jazz pianist, and only began singing because a nightclub owner insisted — it turned out to be the best decision of his life!"},
    {"name": "Perry Como", "era": "1940s–1980s", "category": "Music", "known_for": "Smooth crooner known as 'Mr. C'", "fun_fact": "Perry Como had 42 Top 10 hits in the United States and was the first major artist to have his own television series in the 1940s."},
    # History & World Leaders
    {"name": "Winston Churchill", "era": "1900s–1960s", "category": "History", "known_for": "British wartime Prime Minister and great orator", "fun_fact": "Churchill won the Nobel Prize in Literature in 1953 for his multi-volume history of World War II and his wartime speeches."},
    {"name": "Eleanor Roosevelt", "era": "1930s–1960s", "category": "History", "known_for": "First Lady, diplomat, and champion of human rights", "fun_fact": "Eleanor Roosevelt was the first person to write a syndicated daily newspaper column — 'My Day' — which she wrote for 27 years."},
    {"name": "Queen Elizabeth II", "era": "1952–2022", "category": "History", "known_for": "The longest-reigning British monarch", "fun_fact": "Queen Elizabeth II celebrated 70 years on the throne in 2022, making her the longest-reigning British monarch in history."},
    {"name": "Martin Luther King Jr.", "era": "1950s–1960s", "category": "History", "known_for": "Civil rights leader and Nobel Peace Prize winner", "fun_fact": "Martin Luther King Jr. was just 35 years old when he received the Nobel Peace Prize — the youngest person to receive the award at that time."},
    {"name": "Neil Armstrong", "era": "1960s", "category": "History", "known_for": "First person to walk on the moon", "fun_fact": "Neil Armstrong's famous words on the moon — 'one small step for man' — were heard by over 600 million people watching on television worldwide."},
    {"name": "Amelia Earhart", "era": "1920s–1930s", "category": "History", "known_for": "The first female aviator to fly solo across the Atlantic Ocean", "fun_fact": "Amelia Earhart received her pilot's licence in 1923 — a time when very few women drove cars, let alone flew aeroplanes!"},
    {"name": "Albert Einstein", "era": "1900s–1950s", "category": "History", "known_for": "Theoretical physicist who developed the theory of relativity", "fun_fact": "Einstein did not speak until he was three years old, and some teachers thought he was slow — he later became the most famous scientist in the world."},
    # Sport
    {"name": "Muhammad Ali", "era": "1960s–1980s", "category": "Sport", "known_for": "Three-time World Heavyweight boxing champion", "fun_fact": "Muhammad Ali was so fast in the boxing ring that opponents could barely see his punches coming — he threw up to 8 punches per second!"},
    {"name": "Babe Ruth", "era": "1920s–1930s", "category": "Sport", "known_for": "Baseball legend known as 'The Sultan of Swat'", "fun_fact": "Babe Ruth hit 714 home runs in his career, a record that stood for 39 years. He also pitched very successfully before becoming a full-time slugger."},
    {"name": "Jesse Owens", "era": "1930s", "category": "Sport", "known_for": "Olympic sprinter who won 4 gold medals at the 1936 Berlin Olympics", "fun_fact": "Jesse Owens set three world records and tied a fourth in less than one hour on a single afternoon — a feat never matched in track and field history."},
    {"name": "Pelé", "era": "1950s–1970s", "category": "Sport", "known_for": "Brazilian football legend and three-time World Cup winner", "fun_fact": "Pelé scored over 1,000 goals in his professional career — a record so extraordinary that the exact count is still debated by football fans today!"},
    {"name": "Roger Bannister", "era": "1950s", "category": "Sport", "known_for": "The first person to run a mile in under four minutes", "fun_fact": "Roger Bannister ran the first ever sub-four-minute mile in May 1954. Remarkably, he was a full-time medical student at the time and only trained for 30 minutes a day!"},
    # Science, Arts & Literature
    {"name": "Marie Curie", "era": "1890s–1930s", "category": "Science", "known_for": "Pioneer of radioactivity research, two-time Nobel Prize winner", "fun_fact": "Marie Curie is the only person in history to have won the Nobel Prize in two different sciences — Physics in 1903 and Chemistry in 1911."},
    {"name": "Walt Disney", "era": "1920s–1960s", "category": "Entertainment", "known_for": "Creator of Mickey Mouse and founder of the Disney empire", "fun_fact": "Walt Disney was rejected over 300 times by bankers when he tried to raise money for Disneyland. The park opened in 1955 and became one of the most visited places on Earth."},
    {"name": "Agatha Christie", "era": "1920s–1970s", "category": "Literature", "known_for": "Best-selling mystery novelist and creator of Hercule Poirot and Miss Marple", "fun_fact": "Agatha Christie is the best-selling fiction writer of all time, with over two billion books sold — second only to the Bible and Shakespeare."},
    {"name": "Charlie Chaplin", "era": "1910s–1970s", "category": "Film", "known_for": "Silent film star and comedian who created 'The Tramp'", "fun_fact": "Charlie Chaplin once entered a Charlie Chaplin look-alike contest — and came in third place! Judges did not recognise him without his costume."},
    {"name": "Fred Astaire", "era": "1930s–1980s", "category": "Film & Dance", "known_for": "The greatest dancer in Hollywood history", "fun_fact": "Fred Astaire's first screen test note from an executive said: 'Can't act. Slightly bald. Can dance a little.' He went on to dance in over 30 films!"},
    {"name": "Lucille Ball", "era": "1950s–1970s", "category": "Comedy", "known_for": "Star of 'I Love Lucy', one of the most beloved TV shows ever made", "fun_fact": "Lucille Ball was one of the first women to run a major Hollywood studio — she co-founded Desilu Productions, which produced Star Trek and Mission: Impossible."},
    {"name": "Grace Kelly", "era": "1950s", "category": "Film & Royalty", "known_for": "Hollywood actress who became Princess of Monaco", "fun_fact": "Grace Kelly retired from acting at the height of her fame, at age 26, to marry Prince Rainier III and become the Princess of Monaco."},
    {"name": "Gene Kelly", "era": "1940s–1970s", "category": "Film & Dance", "known_for": "Choreographer and dancer who transformed Hollywood musicals", "fun_fact": "Gene Kelly filmed the iconic 'Singin' in the Rain' dance routine with a 103-degree fever — you would never guess it from watching the scene!"},
    # — second 30 —
    {"name": "Cary Grant", "era": "1930s–1960s", "category": "Film", "known_for": "Debonair Hollywood star and one of the greatest actors of the Golden Age", "fun_fact": "Cary Grant was born Archibald Leach in Bristol, England. He reinvented himself entirely, including his accent, after moving to America."},
    {"name": "Katharine Hepburn", "era": "1930s–1980s", "category": "Film", "known_for": "Four-time Academy Award winner and one of Hollywood's greatest actresses", "fun_fact": "Katharine Hepburn won four Academy Awards for Best Actress — a record that stood for decades and has never been surpassed."},
    {"name": "James Stewart", "era": "1930s–1980s", "category": "Film", "known_for": "Beloved actor famous for It's a Wonderful Life and other classics", "fun_fact": "James Stewart was so uncomfortable being recognised as a star that he insisted his name not appear above the film title on his last few pictures."},
    {"name": "Sophia Loren", "era": "1950s–2000s", "category": "Film", "known_for": "Italian screen legend and the first actor to win an Oscar for a non-English-language performance", "fun_fact": "Sophia Loren was told by a producer early in her career that her nose was too long and her hips too wide. She ignored the advice entirely!"},
    {"name": "Louis Armstrong", "era": "1920s–1970s", "category": "Music", "known_for": "Jazz trumpet master known as Satchmo", "fun_fact": "Louis Armstrong's 'Hello, Dolly!' knocked The Beatles off the No. 1 spot in 1964 — he was 63 years old at the time."},
    {"name": "Ella Fitzgerald", "era": "1930s–1990s", "category": "Music", "known_for": "The First Lady of Song, one of the greatest jazz vocalists of all time", "fun_fact": "Ella Fitzgerald won 13 Grammy Awards and sold over 40 million albums. She could scat-sing so fast that musicians said she was playing an instrument with her voice."},
    {"name": "John Wayne", "era": "1930s–1970s", "category": "Film", "known_for": "Iconic Western and war film actor", "fun_fact": "John Wayne's real name was Marion Robert Morrison. He got the nickname 'Duke' from a dog he owned as a child."},
    {"name": "Marilyn Monroe", "era": "1950s–1960s", "category": "Film", "known_for": "Hollywood icon and one of the most recognisable figures of the 20th century", "fun_fact": "Marilyn Monroe was a serious reader who owned over 400 books. She was known to read heavyweight literature like Ulysses by James Joyce."},
    {"name": "Paul McCartney", "era": "1960s–present", "category": "Music", "known_for": "Beatle, songwriter, and one of the most successful musicians in history", "fun_fact": "Paul McCartney woke up one morning with the complete melody for 'Yesterday' in his head. He thought he must have heard it somewhere and spent weeks asking friends if they recognised it."},
    {"name": "Clint Eastwood", "era": "1960s–present", "category": "Film", "known_for": "Actor and director famous for Westerns and Dirty Harry", "fun_fact": "Clint Eastwood was once elected mayor of Carmel-by-the-Sea, California — he won his campaign partly over a ban on eating ice cream on the street!"},
    {"name": "Audrey Hepburn", "era": "1950s–1990s", "category": "Film", "known_for": "Iconic actress and humanitarian", "fun_fact": "During World War II, Audrey Hepburn survived near-starvation in the Netherlands. She later said her experience gave her a deep connection to the hungry children she helped through UNICEF."},
    {"name": "Tony Bennett", "era": "1950s–2020s", "category": "Music", "known_for": "Legendary crooner and one of the last great traditional pop singers", "fun_fact": "Tony Bennett continued recording albums into his nineties, including a celebrated duet record with Lady Gaga that reached number one in 2021."},
    {"name": "Shirley Temple", "era": "1930s–1940s", "category": "Film", "known_for": "Child star who became the biggest box-office draw in America during the Great Depression", "fun_fact": "Shirley Temple received a special miniature Academy Award at age six — the first ever honorary Oscar — in recognition of her outstanding contribution to screen entertainment."},
    {"name": "Bob Dylan", "era": "1960s–present", "category": "Music", "known_for": "Singer-songwriter and poet who defined a generation", "fun_fact": "Bob Dylan is the only musician to have been awarded the Nobel Prize in Literature, which he received in 2016 for his poetic songwriting."},
    {"name": "Grace Kelly", "era": "1950s–1960s", "category": "Film & Royalty", "known_for": "Oscar-winning actress who became Princess of Monaco", "fun_fact": "Grace Kelly appeared on the cover of over 40 magazines before she was 26 — then gave up Hollywood entirely for royal life in Monaco."},
    {"name": "Sammy Davis Jr.", "era": "1940s–1990s", "category": "Entertainment", "known_for": "Rat Pack entertainer, singer, dancer, actor, and comedian", "fun_fact": "Sammy Davis Jr. lost his left eye in a car accident in 1954. He wore a glass eye for the rest of his life and often joked about it on stage."},
    {"name": "Lena Horne", "era": "1940s–1990s", "category": "Music & Film", "known_for": "Groundbreaking entertainer who fought racial barriers in Hollywood", "fun_fact": "Lena Horne refused to play servant roles in Hollywood films and insisted on being cast in dignified parts — a courageous stand that cost her many opportunities but changed the industry."},
    {"name": "Johnny Cash", "era": "1950s–2000s", "category": "Music", "known_for": "The Man in Black — country music icon", "fun_fact": "Johnny Cash once performed for an audience of just two people when his tour bus broke down in a tiny town. He said it was one of his best shows ever."},
    {"name": "Barbara Stanwyck", "era": "1930s–1980s", "category": "Film", "known_for": "Tough, versatile actress who starred in some of Hollywood's greatest films", "fun_fact": "Barbara Stanwyck learned all her lines — every word — before she arrived on set each day. Directors said she was the most thoroughly prepared actress they had ever worked with."},
    {"name": "Rod Stewart", "era": "1960s–present", "category": "Music", "known_for": "Rock and pop singer with one of the most recognisable voices in music", "fun_fact": "Rod Stewart is a passionate model railway enthusiast who has spent decades building an enormous, incredibly detailed model of a 1940s American city in his attic."},
    {"name": "Tina Turner", "era": "1960s–2000s", "category": "Music", "known_for": "Queen of Rock 'n' Roll — one of the best-selling music artists of all time", "fun_fact": "Tina Turner released her best-selling album 'Private Dancer' at the age of 44, proving that stardom has no age limit."},
    {"name": "Gregory Peck", "era": "1940s–1990s", "category": "Film", "known_for": "Oscar-winning actor best loved for To Kill a Mockingbird", "fun_fact": "Gregory Peck turned down the role of James Bond. He felt it did not suit his quiet, dignified style — and he was probably right!"},
    {"name": "Billie Holiday", "era": "1930s–1950s", "category": "Music", "known_for": "Jazz and blues singer regarded as one of the greatest vocalists of all time", "fun_fact": "Billie Holiday wore a gardenia in her hair on stage not for fashion but necessity — she wore it to cover a burn from a curling iron that she got before a performance."},
    {"name": "Charlton Heston", "era": "1950s–1990s", "category": "Film", "known_for": "Star of epic Hollywood films including Ben-Hur and The Ten Commandments", "fun_fact": "Charlton Heston spent six months learning to drive a chariot to prepare for the famous chariot race in Ben-Hur — the sequence took 10,000 extras and 78 horses to film."},
    {"name": "Ava Gardner", "era": "1940s–1970s", "category": "Film", "known_for": "One of Hollywood's most glamorous stars of the Golden Age", "fun_fact": "Ava Gardner was discovered by MGM after a photo of her appeared in a shop window. She was 18 years old and had never acted before."},
    {"name": "Yogi Berra", "era": "1940s–1960s", "category": "Sport", "known_for": "Baseball catcher and three-time MVP famous for his witty sayings", "fun_fact": "Yogi Berra won more World Series rings than any other player in history — 10 in total. He was also famous for sayings like 'It ain't over till it's over.'"},
    {"name": "Eartha Kitt", "era": "1950s–2000s", "category": "Music & Film", "known_for": "Singer and actress famous for her purring voice and unforgettable stage presence", "fun_fact": "Eartha Kitt was banned from the White House for 10 years after she spoke out against the Vietnam War at a luncheon hosted by Lady Bird Johnson in 1968."},
    {"name": "Sean Connery", "era": "1960s–2000s", "category": "Film", "known_for": "The original James Bond, and one of cinema's most charismatic stars", "fun_fact": "Before becoming an actor, Sean Connery worked as a milkman, a bricklayer, and a Royal Navy sailor. He only took up acting in his twenties."},
    {"name": "Doris Day", "era": "1940s–1980s", "category": "Film & Music", "known_for": "Beloved actress and singer of the Golden Hollywood era", "fun_fact": "Doris Day's birth name was Doris Mary Ann Kappelhoff. She took the stage name Day from a song called 'Day by Day' that she sang at auditions."},
    {"name": "Louis Prima", "era": "1930s–1970s", "category": "Music", "known_for": "Energetic trumpet player, singer, and bandleader beloved for his joyful showmanship", "fun_fact": "Louis Prima's song 'Just a Gigolo' became a hit again 30 years after his death — proving great music never really goes out of style."},
]


class FamousFaceProvider(BaseCareCircleProvider):
    provider_key = "famous_face"
    is_safe_for_patient = True

    """
    Presents a familiar person from history, entertainment, or sport with a fun fact.
    Pure static provider — 30 famous faces from the 20th century in the curated pool.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pool = cfg.get("faces", FAMOUS_FACES)
        entry = date_seeded_choice(pool, self.get_generation_date())
        return {
            "name": entry["name"],
            "era": entry["era"],
            "category": entry["category"],
            "known_for": entry["known_for"],
            "fun_fact": entry["fun_fact"],
        }
