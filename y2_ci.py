import json
import os
import sys
import yt_dlp

PASTA = "videos"
ARQUIVO_JSON = "playlist.json"

URL = os.environ["PLAYLIST_URL"]
SELECAO = os.environ.get("SELECAO", "todos").strip().lower()
QUALIDADE = os.environ.get("QUALIDADE", "720").strip()

COOKIES = "cookies.txt" if os.path.exists("cookies.txt") else None

FORMATOS = {
    "360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "melhor": "bestvideo+bestaudio/best",
}

os.makedirs(PASTA, exist_ok=True)


def base_opts():
    opts = {"quiet": True, "js_runtimes": {"node": {}}}
    if COOKIES:
        opts["cookiefile"] = COOKIES
    return opts


def listar_playlist():
    opts = base_opts() | {"extract_flat": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(URL, download=False)

    videos = []
    for e in info.get("entries") or [info]:
        if not e:
            continue
        videos.append({
            "titulo": e.get("title"),
            "url": e.get("url") or e.get("webpage_url"),
            "duracao": e.get("duration"),
            "baixado": False,
        })
    return info.get("title", "Playlist"), videos


def escolher(total):
    if SELECAO == "todos":
        return list(range(total))
    indices = set()
    for n in SELECAO.split(","):
        n = int(n.strip())
        if 1 <= n <= total:
            indices.add(n - 1)
        else:
            print(f"Número ignorado: {n}")
    return sorted(indices)


def main():
    if QUALIDADE not in FORMATOS:
        sys.exit(f"Qualidade inválida: {QUALIDADE}")

    nome, videos = listar_playlist()
    print(f"Playlist: {nome} ({len(videos)} vídeos)")

    erros = 0
    for i in escolher(len(videos)):
        v = videos[i]
        print(f"\n[{i + 1}/{len(videos)}] A baixar: {v['titulo']}")
        opts = base_opts() | {
            "quiet": False,
            "format": FORMATOS[QUALIDADE],
            "outtmpl": os.path.join(PASTA, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "noplaylist": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([v["url"]])
            v["baixado"] = True
        except Exception as erro:
            erros += 1
            print(f"Erro ao baixar: {erro}")

    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump({"playlist": nome, "videos": videos},
                  f, ensure_ascii=False, indent=4)

    if not any(v["baixado"] for v in videos):
        sys.exit("Nenhum vídeo foi baixado.")
    print(f"\nConcluído. Erros: {erros}")


if __name__ == "__main__":
    main()
