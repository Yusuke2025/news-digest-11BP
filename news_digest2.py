import feedparser
import datetime
import requests
from jinja2 import Template
import os
import google.generativeai as genai

CONFIG = {
    "rss_feeds": {
        "電通": "https://www.google.com/alerts/feeds/16026360528624384949/10928416445605670714",
        "ソフトバンク": "https://www.google.com/alerts/feeds/16026360528624384949/6763738800941277814",
        "LINEヤフー": "https://www.google.com/alerts/feeds/16026360528624384949/7803140798119325522",
        "大正製薬": "https://www.google.com/alerts/feeds/16026360528624384949/16372116154633207855"
    },
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", "AIzaSyCOzY-MxzAjOpTN0DfzOlysnwyVfl7oLnY"),
    "output_file": "index.html"  # GitHub Pagesのため変更
}

def get_daily_quote():
    """日本で認知度の高い有名人の格言を日替わりで取得"""
    # 日本で認知度の高い有名人の格言リスト
    quotes = [
        {"quote": "しあわせはいつも自分のこころがきめる", "author": "相田みつを"},
        {"quote": "努力は必ず報われる。もし報われない努力があるのならば、それはまだ努力と呼べない", "author": "王貞治"},
        {"quote": "成功の反対は失敗ではなく「やらないこと」だ", "author": "佐々木則夫"},
        {"quote": "自分が幸せかどうかは、自分で決めるしかないのよ", "author": "マツコ・デラックス"},
        {"quote": "何かを捨てないと前に進めない", "author": "スティーブ・ジョブズ"},
        {"quote": "為せば成る、為さねば成らぬ。何事も成らぬは人の為さぬなり", "author": "上杉鷹山"},
        {"quote": "やってみせ、言って聞かせて、させてみせ、褒めてやらねば人は動かじ", "author": "山本五十六"},
        {"quote": "面白きこともなき世を面白く住みなすものは心なりけり", "author": "高杉晋作"},
        {"quote": "夢なき者に成功なし", "author": "吉田松陰"},
        {"quote": "初心を忘れないことっていうのは大事ですが、初心でプレイをしていてはいけないのです", "author": "イチロー"},
        {"quote": "妥協はたくさんしてきた。自分に負けたこともたくさんあります。ただ野球に関してはそれがない", "author": "イチロー"},
        {"quote": "失敗と書いて成功と読む", "author": "野村克也"},
        {"quote": "勝ちに不思議の勝ちあり。負けに不思議の負けなし", "author": "野村克也"},
        {"quote": "芸術は爆発だ！", "author": "岡本太郎"},
        {"quote": "人間が人間のことを想う、これ以上に美しいものはない", "author": "高倉健"},
        {"quote": "真の富とは道徳に基づくものでなければ決して永くは続かない", "author": "渋沢栄一"},
        {"quote": "石の上にも三年という。しかし、三年を一年で習得する努力を怠ってはならない", "author": "松下幸之助"},
        {"quote": "雨にも負けず 風にも負けず", "author": "宮沢賢治"},
        {"quote": "千日の稽古をもって鍛となし、万日の稽古をもって錬となす", "author": "宮本武蔵"},
        {"quote": "一度地獄を見ると、世の中につらい仕事はなくなるんです", "author": "池上彰"},
        {"quote": "プロはいかなる時でも、言い訳をしない", "author": "千代の富士"},
        {"quote": "人を信じよ、しかし、その百倍も自らを信じよ", "author": "手塚治虫"},
        {"quote": "何かを始めることはやさしいが、それを継続することは難しい。成功させることはなお難しい", "author": "津田梅子"},
        {"quote": "失敗した所で止めるから失敗になる。成功するところまで続ければ成功になる", "author": "松下幸之助"},
        {"quote": "才能とは、情熱を持続させる能力のこと", "author": "宮崎駿"},
        {"quote": "全盛期？これからだよ", "author": "三浦知良"},
        {"quote": "ズルはできない、俺が見てるから", "author": "松井秀喜"},
        {"quote": "この一球は絶対無二の一球なり", "author": "福田雅之助"},
        {"quote": "夢はいつも好きから始まるんです", "author": "澤穂希"},
        {"quote": "輝ける場は人それぞれ。いかに輝くかはその人次第だと思います", "author": "高橋尚子"},
        {"quote": "当たり前のことを言っていたのでは、当たり前の結果しか残せない", "author": "中田英寿"}
    ]
    
    # 日付を基にした固定のインデックスを計算（年月日の合計を格言数で割った余り）
    today = datetime.datetime.now()
    day_index = (today.year + today.month + today.day) % len(quotes)
    selected_quote = quotes[day_index]
    
    quote_text = f"「{selected_quote['quote']}」 - {selected_quote['author']}"
    debug_info = f"<details><summary>格言詳細</summary><pre>選択された格言: {day_index + 1}/{len(quotes)}\n日付: {today.strftime('%Y年%m月%d日')}</pre></details>"
    
    return quote_text, debug_info

def get_daily_story():
    """Gemini APIを使用して日替わりの創作ショートストーリーを生成"""
    try:
        # Gemini APIの設定
        genai.configure(api_key=CONFIG["gemini_api_key"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # 日付に基づいたシード値を生成
        today = datetime.datetime.now()
        seed = (today.year + today.month + today.day) % 100
        
        # ストーリーのテーマリスト
        themes = [
            "電車で偶然出会った二人の5分間の会話",
            "コンビニで夜勤をする店員の不思議な体験",
            "雨の日のバス停で起こった小さな奇跡",
            "図書館で見つけた古い本に挟まれていた手紙",
            "エレベーターに閉じ込められた見知らぬ二人",
            "深夜のラジオ番組に寄せられた謎の投稿",
            "公園のベンチに座る老人と迷子の猫",
            "最終電車で帰宅する会社員の心の声",
            "カフェで隣の席から聞こえてきた会話",
            "病院の待合室で出会った親子の物語"
        ]
        
        # 日付に基づいてテーマを選択
        theme_index = seed % len(themes)
        selected_theme = themes[theme_index]
        
        # プロンプトを作成
        prompt = f"""
以下の設定で、150文字程度の創作ショートストーリーを書いてください。

設定：{selected_theme}

条件：
- 150文字前後（100-200文字以内）
- 読者の想像力を刺激する内容
- 心に残る印象的な結末
- 日本語で自然な文章
- 改行は使わず、一続きの文章で
"""
        
        response = model.generate_content(prompt)
        story_text = response.text.strip()
        
        # 文字数制限チェック（200文字を超える場合は切り詰める）
        if len(story_text) > 200:
            story_text = story_text[:197] + "..."
        
        debug_info = f"<details><summary>ストーリー詳細</summary><pre>テーマ: {selected_theme}\n文字数: {len(story_text)}文字\n生成日: {today.strftime('%Y年%m月%d日')}</pre></details>"
        
        return story_text, debug_info
        
    except Exception as e:
        # APIエラー時のフォールバック
        fallback_stories = [
            "駅のホームで電車を待っていると、隣に立った見知らぬ女性が小さくつぶやいた。「今日で最後なんです」。彼女の手には転職届けが握られていた。電車が来ると、彼女は振り返って微笑んだ。「新しい人生、頑張ります」。その笑顔に、僕も勇気をもらった。",
            "深夜のコンビニで、レジの前に立つ老人が千円札を数えている。「あと50円足りないな」。後ろに並んでいた学生が、そっと50円玉を差し出した。「おじいちゃん、落としましたよ」。老人は嬉しそうに頷き、温かいコーヒーを買って帰っていった。",
            "図書館で古い詩集を開くと、栞代わりに挟まれた写真が落ちた。若い男女が笑顔で写っている。裏には「永遠に」と書かれていた。司書に渡すと、彼女は驚いた表情を見せた。「これ、私の両親です」。運命的な再会に、二人は静かに微笑んだ。"
        ]
        
        story_index = (datetime.datetime.now().day) % len(fallback_stories)
        story_text = fallback_stories[story_index]
        debug_info = f"<details><summary>ストーリー詳細</summary><pre>フォールバック使用\nエラー: {str(e)}\n生成日: {datetime.datetime.now().strftime('%Y年%m月%d日')}</pre></details>"
        
        return story_text, debug_info

def fetch_news(feed_url):
    """RSSニュースを取得（24時間以内のみ）"""
    news_list = []
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            try:
                published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                if (now - published).total_seconds() <= 86400:
                    news_list.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": getattr(entry, 'summary', ''),
                        "published": published.astimezone().strftime("%Y-%m-%d %H:%M")
                    })
            except Exception:
                continue
    except Exception:
        pass
    return news_list

def category_id(category):
    """HTMLのid属性用"""
    return (
        "dentsu" if category == "電通"
        else "softbank" if category == "ソフトバンク"
        else "lineyahoo" if category == "LINEヤフー"
        else "taishoseiyaku" if category == "大正製薬"
        else category.lower()
    )

def generate_html(categorized_news, daily_quote, quote_debug, daily_story, story_debug, output_path):
    html_template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>11BP 生成AI勉強会 NEWS DIGEST</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #fff; color: #111; font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; }
        .page-title { font-size: 2.2em; font-weight: bold; letter-spacing: 0.08em; margin: 0; padding: 32px 0 8px 0; text-align: center; }
        .navbar { background: #fff; border-bottom: 1px solid #eee; padding: 18px 0; display: flex; justify-content: center; gap: 40px; position: sticky; top: 0; z-index: 100; }
        .navbar a { color: #111; text-decoration: none; font-weight: bold; font-size: 1.1em; letter-spacing: 0.1em; transition: color 0.2s; }
        .navbar a:hover { color: #666; }
        .container { max-width: 900px; margin: 40px auto; padding: 0 24px; }
        .section { margin-bottom: 48px; scroll-margin-top: 80px; }
        h2 { font-size: 1.3em; border-left: 4px solid #111; padding-left: 12px; margin: 32px 0 18px 0; }
        .daily-quote { background: #f5f5f5; border-radius: 10px; padding: 20px 28px; margin-bottom: 24px; font-size: 1.1em; }
        .daily-story { background: #f0f8ff; border-radius: 10px; padding: 20px 28px; margin-bottom: 36px; font-size: 1.05em; line-height: 1.6; }
        .story-title { font-weight: bold; color: #2c5aa0; margin-bottom: 12px; }
        ul.news-list { list-style: none; padding: 0; }
        ul.news-list li { margin-bottom: 20px; padding: 16px; border-radius: 8px; transition: background 0.2s; }
        ul.news-list li:hover { background: #f8f8f8; }
        .news-title { font-weight: bold; font-size: 1.05em; color: #111; text-decoration: none; }
        .news-title:hover { color: #666; }
        .news-meta { color: #888; font-size: 0.95em; margin-top: 2px; }
        .news-summary { margin: 4px 0 0 0; font-size: 1em; }
        .more-btn { background: #fff; color: #111; border: 1px solid #aaa; border-radius: 6px; padding: 8px 20px; font-size: 1em; cursor: pointer; margin: 10px 0 0 0; transition: background 0.2s; }
        .more-btn:hover { background: #f0f0f0; }
        .hidden { display: none; }
        pre { font-size: 0.8em; color: #666; background: #f8f8f8; border: 1px solid #eee; padding: 8px; border-radius: 4px; overflow-x: auto; max-height: 200px; }
        details { margin-top: 8px; }
        summary { cursor: pointer; color: #666; font-size: 0.9em; }
        @media (max-width: 600px) {
            .navbar { flex-direction: column; gap: 12px; padding: 12px 0; }
            .container { padding: 0 8px; }
        }
    </style>
</head>
<body>
    <div id="top"></div>
    <div class="page-title">11BP 生成AI勉強会 NEWS DIGEST</div>
    <nav class="navbar">
        <a href="#top">TOP</a>
        <a href="#dentsu">電通</a>
        <a href="#softbank">ソフトバンク</a>
        <a href="#lineyahoo">LINEヤフー</a>
        <a href="#taishoseiyaku">大正製薬</a>
    </nav>
    <div class="container">
        <div class="daily-quote">
            <span>今日の格言</span><br>
            <strong>{{ daily_quote }}</strong>
            {{ quote_debug|safe }}
        </div>
        <div class="daily-story">
            <div class="story-title">今日の創作ショートストーリー</div>
            {{ daily_story }}
            {{ story_debug|safe }}
        </div>
        {% for category, news_list in categorized_news.items() %}
        <div class="section" id="{{ category_id(category) }}">
            <h2>{{ category }} ({{ news_list|length }}件)</h2>
            <ul class="news-list">
                {% for news in news_list[:5] %}
                <li>
                    <a class="news-title" href="{{ news.link }}" target="_blank">{{ news.title }}</a>
                    <div class="news-meta">{{ news.published }}</div>
                    <div class="news-summary">{{ news.summary | safe }}</div>
                </li>
                {% endfor %}
                {% if news_list|length > 5 %}
                <div id="more-{{ category_id(category) }}" class="hidden">
                    {% for news in news_list[5:] %}
                    <li>
                        <a class="news-title" href="{{ news.link }}" target="_blank">{{ news.title }}</a>
                        <div class="news-meta">{{ news.published }}</div>
                        <div class="news-summary">{{ news.summary | safe }}</div>
                    </li>
                    {% endfor %}
                </div>
                <button class="more-btn" onclick="toggleMore('{{ category_id(category) }}', this)">もっと見る</button>
                {% endif %}
                {% if news_list|length == 0 %}
                <li>直近24時間以内のニュースはありません。</li>
                {% endif %}
            </ul>
        </div>
        {% endfor %}
    </div>
    <script>
        function toggleMore(category, btn) {
            var moreDiv = document.getElementById('more-' + category);
            if (moreDiv.classList.contains('hidden')) {
                moreDiv.classList.remove('hidden');
                btn.textContent = '閉じる';
            } else {
                moreDiv.classList.add('hidden');
                btn.textContent = 'もっと見る';
            }
        }
    </script>
</body>
</html>
    """
    template = Template(html_template)
    html = template.render(
        categorized_news=categorized_news,
        daily_quote=daily_quote,
        quote_debug=quote_debug,
        daily_story=daily_story,
        story_debug=story_debug,
        category_id=category_id
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[SUCCESS] HTMLファイルを生成しました: {os.path.abspath(output_path)}")

def main():
    print("[INFO] ニュースクリッピング開始...")
    order = ["電通", "ソフトバンク", "LINEヤフー", "大正製薬"]
    categorized_news = {}
    for category in order:
        url = CONFIG["rss_feeds"].get(category)
        categorized_news[category] = fetch_news(url) if url else []
        print(f"[INFO] {category}: {len(categorized_news[category])}件のニュースを取得")
    
    daily_quote, quote_debug = get_daily_quote()
    daily_story, story_debug = get_daily_story()
    generate_html(categorized_news, daily_quote, quote_debug, daily_story, story_debug, CONFIG["output_file"])
    print("[INFO] 処理完了！")

if __name__ == "__main__":
    main()
