This is mainly for talking to chatbots that have huge context but don't automatically download code from github.

example use:

```
python github2file.py https://github.com/huggingface/transformers
```

now you can drop transformers.txt into your conversation with Claude, etc.

For a private repository, you can use the following format:
```
python github2file.py https://<USERNAME>:<GITHUB_ACCESS_TOKEN>@github.com/huggingface/transformers
```
