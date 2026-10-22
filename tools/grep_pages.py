"""Search pdftotext outputs page by page (pages split at form feeds) and print file, PDF page and the matching line.
Usage: python3 tools/grep_pages.py '<regex>' [--max N] file1.txt [file2.txt ...]   (case-insensitive)"""
import re, sys, pathlib

args = sys.argv[1:]
pat = re.compile(args.pop(0), re.I)
mx = 8
if args and args[0] == "--max":
    args.pop(0); mx = int(args.pop(0))
for f in args:
    text = pathlib.Path(f).read_text(errors="replace")
    hits = 0
    for pno, page in enumerate(text.split("\f"), 1):
        for line in page.splitlines():
            if pat.search(line):
                hits += 1
                if hits <= mx:
                    print(f"{pathlib.Path(f).stem} p.{pno}: {' '.join(line.split())[:220]}")
    if hits > mx:
        print(f"{pathlib.Path(f).stem}: ... {hits - mx} more hits")
    if hits == 0:
        print(f"{pathlib.Path(f).stem}: 0 hits")
