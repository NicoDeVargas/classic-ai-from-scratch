import os
import subprocess

import imageio_ffmpeg

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(os.path.dirname(AQUI), "saida")
IMG = os.path.join(AQUI, "img")
SEGUNDO = 12

if __name__ == "__main__":
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for nome in sorted(os.listdir(SAIDA)):
        if not nome.endswith(".mp4"):
            continue
        destino = os.path.join(IMG, "capa_" + nome[:-4] + ".png")
        subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-ss", str(SEGUNDO), "-i",
                        os.path.join(SAIDA, nome), "-frames:v", "1", destino], check=True)
        print("capa:", destino)
