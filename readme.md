# KoiAnalyser

A simple tool to extract character data and resources from character PNG files. Currently it outputs a summery to the console and a complete parameter tree to `*._settings.txt`. Additionally all embedded PNG textures are dumped as well, with the parameter tree containing a MD5 hash instead.

The main idea with this tool is to get an understanding on why some character files are huge, and to provide a way to diff two similar cards to see what has been changed.

## Usage

```bash
python main.py "some_card.png"
```
