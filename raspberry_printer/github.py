from datetime import datetime


def make_github_new_text(data):
    info_type = data.get("info_type")
    repo = data.get("repo")
    if not info_type and not repo:
        return ""
    title = data.get("title", "")
    content = data.get("content", "")
    info_repo = f"REPO: {repo}\n"
    info_time = str(datetime.now()) + "\n\n"
    info_start = f"新的 {info_type.upper()} 来了来了来了！\n\n"
    info_title = f"{info_type.upper()} Title: {title}\n"
    info_content = f"Content:\n {content}"
    return info_time + info_repo + info_start + info_title + info_content
