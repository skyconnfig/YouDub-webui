import bilibili_toolman.bilisession.web as m
import os
import json

path = m.__file__
with open(path, encoding='utf-8') as f:
    content = f.read()

# Fix 1: KeyError: 'OK' and response format issues
old_block = """        state = self._upload_status(
            endpoint, basename, config["upload_id"], config["biz_id"]
        )
        if state["OK"] == 1:
            self.logger.debug("上传完毕: %s" % ReprExDict(state))
        else:
            raise Exception("上传失败: %s" % ReprExDict(state))
        return endpoint, config["biz_id"]"""

new_block = """        state = self._upload_status(
            endpoint, basename, config["upload_id"], config["biz_id"]
        )
        if isinstance(state, str):
            try:
                state = json.loads(state)
            except:
                pass

        # 兼容不同的返回格式: 有时是 OK (1), 有时是 code (0), 或者是 OK (True)
        is_ok = False
        if isinstance(state, dict):
            if state.get("OK") == 1 or state.get("OK") is True:
                is_ok = True
            elif state.get("code") == 0 or state.get("Code") == 0:
                is_ok = True
            elif not state: 
                is_ok = False 

        if is_ok:
            self.logger.debug("上传完毕: %s" % ReprExDict(state))
        else:
            raise Exception("上传失败: %s" % (ReprExDict(state) if isinstance(state, dict) else state))
        return endpoint, config["biz_id"]"""

# Fix 2: Stability improvements for weak network
old_params = """    RETRIES_UPLOAD_ID = 5

    DELAY_FETCH_UPLOAD_ID = 0.1
    DELAY_RETRY_UPLOAD_ID = 1
    DELAY_REPORT_PROGRESS = 1

    RETRIES_VIDEO_SUBMISSION = 5
    DELAY_VIDEO_SUBMISSION = 30

    WORKERS_UPLOAD = 3"""

new_params = """    RETRIES_UPLOAD_ID = 10
    DELAY_RETRY_UPLOAD_ID = 5
    WORKERS_UPLOAD = 1"""

# Fix 3: Handle dirty chunks properly
old_dirty = """        if tConsume.dirty:
            self.logger.error("部分上传分块存在问题，稿件可能永不过审!")  # oh no
        return True"""

new_dirty = """        if tConsume.dirty:
            self.logger.error("部分上传分块存在问题，稿件可能永不过审!")  # oh no
            return False
        return True"""

# Fix 4: Interrupt on failed chunks
old_inter = """        self._upload_chunks_to_endpoint_blocking(chunks)
        \"\"\"Wait for current upload to finish\"\"\"
        file_manager.close(path)"""

new_inter = """        success = self._upload_chunks_to_endpoint_blocking(chunks)
        \"\"\"Wait for current upload to finish\"\"\"
        file_manager.close(path)
        if not success:
            raise Exception("视频分块上传失败，已中断。")"""

changed = False
if old_block in content:
    content = content.replace(old_block, new_block)
    print("Patched Fix 1 (Response Format)")
    changed = True

if old_params in content:
    content = content.replace(old_params, new_params)
    print("Patched Fix 2 (Stability Params)")
    changed = True

if old_dirty in content:
    content = content.replace(old_dirty, new_dirty)
    print("Patched Fix 3 (Dirty Counter)")
    changed = True

if old_inter in content:
    content = content.replace(old_inter, new_inter)
    print("Patched Fix 4 (Failure Interruption)")
    changed = True

if changed:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved all patches to: {path}")
else:
    print("No changes made - file may already be fully patched or patterns mismatched")
