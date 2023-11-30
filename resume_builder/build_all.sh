python3 md_generator.py
python3 cover-letter_generator.py
python3 html_generator.py
pandoc resume.md -f markdown -t html -c resume-stylesheet.css -s -o resume.html
wkhtmltopdf --enable-local-file-access resume.html ../resume.pdf 
pandoc coverletter.md -f markdown -t html -c resume-stylesheet.css -s -o coverletter.html
wkhtmltopdf --enable-local-file-access coverletter.html ../coverletter.pdf 