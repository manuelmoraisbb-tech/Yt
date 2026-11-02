name: Baixar vídeos do YouTube

on:
  workflow_dispatch:
    inputs:
      playlist_url:
        description: "URL da playlist (ou de um vídeo)"
        required: true
      selecao:
        description: "Vídeos a baixar (ex.: 1,3,5 ou todos)"
        default: "todos"
      qualidade:
        description: "Qualidade"
        type: choice
        default: "720"
        options: ["360", "480", "720", "1080", "melhor"]

jobs:
  baixar:
    runs-on: ubuntu-latest
    timeout-minutes: 360
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Instalar dependências
        run: |
          pip install -U "yt-dlp[default]"
          sudo apt-get install -y zip ffmpeg

      - name: Cookies (opcional)
        env:
          YT_COOKIES: ${{ secrets.YT_COOKIES }}
        run: |
          if [ -n "$YT_COOKIES" ]; then
            printf '%s' "$YT_COOKIES" > cookies.txt
          fi

      - name: Baixar vídeos
        env:
          PLAYLIST_URL: ${{ inputs.playlist_url }}
          SELECAO: ${{ inputs.selecao }}
          QUALIDADE: ${{ inputs.qualidade }}
        run: python y2_ci.py

      - name: Criar ZIP
        run: |
          rm -f cookies.txt
          zip -0 -r videos.zip videos playlist.json

      - name: Enviar ZIP
        uses: actions/upload-artifact@v4
        with:
          name: videos
          path: videos.zip
          compression-level: 0
          retention-days: 7
