Credit to PokeAPI for supplying both the images and the API this program uses to fetch information.



## HOW TO USE .trainedddata

1. Install Tesseract-OCR.

2. Navigate to your Tesseract-OCR tessdata folder:
`C:\Program Files\Tesseract-OCR\tessdata`

3. Drop `pokemon.traineddata` into this folder.

4. Verify this worked by running:
`tesseract --list-langs`

5. You should see `pokemon` as an option.

6. Set `OPENAI_API_KEY` as an environment variable in your terminal.

7. Run the program: `python ./main.py`

8. Select the area where the pokemon name and level will appear.
