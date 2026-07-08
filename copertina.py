from PIL import Image, ImageDraw, ImageFont

def aggiungi_titolo(percorso_immagine, titolo, output="copertina_output.png"):
    img = Image.open(percorso_immagine).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    larghezza, altezza = img.size
    draw.text((larghezza // 4, altezza // 10), titolo, fill="white", font=font)
    img.save(output)
    print(f"Salvato: {output}")

if __name__ == "__main__":
    aggiungi_titolo("foto_bici.jpg", "Il Paradosso del Limite")
