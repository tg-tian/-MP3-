import base64
import json
import uuid
import requests
import re
import os
from pydub import AudioSegment

# 语音合成函数
def tts_request(
    text,
    output_path
):
    appid = "4001863206"
    access_token= "sfxRn5j3t9vSiXAL9CgHcr2MJEIlWF1D"
    cluster = "volcano_icl"
    uid = "ark-experience-voice-clone-2109077295"
    host = "openspeech.bytedance.com"
    voice_type = "S_X976hfIy1"
    api_url = f"https://{host}/api/v1/tts"
    header = {"Authorization": f"Bearer;{access_token}"}
    request_json = {
        "app": {
            "appid": appid,
            "token": access_token,
            "cluster": cluster
        },
        "user": {
            "uid": uid
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",
            "speed_ratio": 1.1,
            "volume_ratio": 1.0,
            "pitch_ratio": 1.0,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": "plain",
            "operation": "query",
            "with_frontend": 1,
            "frontend_type": "unitTson"
        }
    }
    try:
        resp = requests.post(api_url, json.dumps(request_json), headers=header)
        if "data" in resp.json():
            data = resp.json()["data"]
            with open(output_path, "wb") as file_to_save:
                file_to_save.write(base64.b64decode(data))
    except Exception as e:
        print(e)

def merge_mp3_by_timestamps(output_dir,file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        input_text = f.read()
    pattern = r"\*\*(\d{2})\:(\d{2}):(\d{2})\*\*\s+“(.*?)”"
    matches = re.findall(pattern, input_text)
    timestamps_ms = []
    for mm, ss, ff, text in matches:
        total_ms = int(mm) * 60_000 + int(ss) * 1000 + int(ff) * 33
        timestamps_ms.append(total_ms)
    # 读取 output_dir 下所有 mp3 文件并按文件名排序
    mp3_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3') and f != "配音.mp3"]
    mp3_files.sort(key=lambda x: int(x.split('_')[0]))
    mp3_paths = [os.path.join(output_dir, f) for f in mp3_files]
    merged = AudioSegment.silent(duration=0)
    current_pos = 0
    for mp3_path, ts in zip(mp3_paths, timestamps_ms):
        # 加入静音补位
        if ts > current_pos:
            silence = AudioSegment.silent(duration=ts - merged.duration_seconds * 1000)
            merged += silence
        seg = AudioSegment.from_mp3(mp3_path)
        merged += seg
        current_pos = ts + len(seg)  # 更新时间位置
    merged += AudioSegment.silent(30000)
    output_path = os.path.join(output_dir, "配音.mp3")
    merged.export(output_path, format="mp3")

#解析解说词文件
def parse_script_file(file_path,output_dir):
    with open(file_path, "r", encoding="utf-8") as f:
        input_text = f.read()

    pattern = r"\*\*(\d{2})\:(\d{2}):(\d{2})\*\*\s+“(.*?)”"
    matches = re.findall(pattern, input_text)

    timestamps_ms = []
    texts = []

    for mm, ss, ff, text in matches:
        total_ms = int(mm) * 60_000 + int(ss) * 1000 + int(ff) * 33
        timestamps_ms.append(total_ms)
        texts.append(text)

    for idx, text in enumerate(texts):
        mp3_path = os.path.join(output_dir, f"{idx}_{text}.mp3")
        tts_request(text=text, output_path=mp3_path)
    # merge_mp3_by_timestamps(output_dir,file_path)
    
# 主函数
file_path = r"C:\低代码视频剪辑素材\配音\讲解词.txt"
output_dir = r"C:\低代码视频剪辑素材\配音\female"
# tts_request("阶段一的目标是构建一个支持场景开发的低代码平台。",r"c:\1.mp3")
# parse_script_file(file_path,output_dir)
# merge_mp3_by_timestamps(output_dir,file_path)
