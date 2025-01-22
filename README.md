CVAF

```bash
docker run --gpus all \
    -v $HOME/.cache/huggingface/hub:/home/computeruse/.cache/huggingface/hub \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -it cvaf
```
