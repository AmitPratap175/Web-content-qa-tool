import re
from pathlib import Path
from app.config import CONFIG

class MarkdownCleaner:
    def __init__(self):
        self.input_dir = Path(CONFIG.SCRAPED_DIR)
        self.output_dir = Path(CONFIG.DOCUMENTS_DIR)
        self.url_pattern = re.compile(r'https?://\S+')
        self.html_tag_pattern = re.compile(r'<.*?>')
        self.markdown_pattern = re.compile(
            r'(\*{1,2}|#{1,6}|\[.*?\]\(.*?\)|`{1,3}.*?`{1,3}|!\[.*?\]\(.*?\))'
        )
        self.code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
        self.non_text_pattern = re.compile(r'[^A-Za-z0-9\s.,;:\'\"!?()\[\]]')

    async def clean_text(self, text: str) -> str:
        text = self.code_block_pattern.sub('', text)
        text = self.url_pattern.sub('', text)
        text = self.html_tag_pattern.sub('', text)
        text = self.markdown_pattern.sub('', text)
        text = self.non_text_pattern.sub(' ', text)
        text = text.replace('(', '').replace(')', '')
        text = text.replace('[', '').replace(']', '')
        text = text.replace('!', '')
        # text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # multiple newlines → one
        text = text.strip()
        return text

    async def process_files(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for md_file in self.input_dir.rglob('*.md'):
            with md_file.open('r', encoding='utf-8') as f:
                raw_text = f.read()

            cleaned_text = await self.clean_text(raw_text)

            output_file = self.output_dir / f"{md_file.stem}_cleaned.md"
            with output_file.open('w', encoding='utf-8') as out_f:
                out_f.write(cleaned_text)

            print(f"[✔] Cleaned: {md_file.name} → {output_file.name}")

    # def clean_text(self, text: str) -> str:
    #     # Remove code blocks
    #     text = self.code_block_pattern.sub('', text)

    #     # Replace inline links [text](url) with just 'text'
    #     text = self.inline_link_pattern.sub(r'\1', text)

    #     # Remove URLs
    #     text = self.url_pattern.sub('', text)

    #     # Remove HTML tags
    #     text = self.html_tag_pattern.sub('', text)

    #     # Remove markdown decorations (bold, italic, code, images, headings)
    #     text = self.markdown_pattern.sub('', text)

    #     # Remove paired single quotes around words (but not apostrophes in contractions)
    #     text = self.paired_single_quotes_pattern.sub(r'\1', text)

    #     # Remove all brackets and parentheses
    #     text = text.replace('(', '').replace(')', '')
    #     text = text.replace('[', '').replace(']', '')
    #     text = text.replace('!', '')

    #     # Remove non-text characters (preserve apostrophes!)
    #     text = self.non_text_pattern.sub(' ', text)

    #     # Collapse multiple whitespace
    #     # text = re.sub(r'\s+', ' ', text).strip()

    #     # Collapse multiple spaces but preserve newlines
    #     text = re.sub(r'[ \t]+', ' ', text)
    #     text = re.sub(r'\n\s*\n+', '\n\n', text)  # multiple newlines → one
    #     text = text.strip()


    #     return text

    # def process_files(self) -> None:
    #     self.output_dir.mkdir(parents=True, exist_ok=True)

    #     for md_file in self.input_dir.rglob('*.md'):
    #         with md_file.open('r', encoding='utf-8') as f:
    #             raw_text = f.read()

    #         cleaned_text = self.clean_text(raw_text)

    #         output_file = self.output_dir / f"{md_file.stem}_cleaned.md"
    #         with output_file.open('w', encoding='utf-8') as out_f:
    #             out_f.write(cleaned_text)

    #         print(f"[✔] Cleaned: {md_file.name} → {output_file.name}")

# --- Hardcoded paths ---
# INPUT_DIR = "./data"     # Change this to your actual path
# OUTPUT_DIR = "./data_processed"       # Change this to your desired output path

# # --- Run ---
# if __name__ == "__main__":
#     cleaner = MarkdownCleaner(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR)
#     cleaner.process_files()
