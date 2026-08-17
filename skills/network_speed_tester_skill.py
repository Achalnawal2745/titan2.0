import speedtest
import urllib.request
import time
import io # Explicitly import io

def run():
    """
    Measures download and upload speed using speedtest-cli with HTTP fallback.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        down = st.download() / (1024 * 1024)
        up = st.upload() / (1024 * 1024)
        return f"Download: {down:.2f} Mbps, Upload: {up:.2f} Mbps"
    except Exception as e:
        try:
            url = "http://speedtest.tele2.net/10MB.zip"
            start = time.time()
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read()
            elapsed = time.time() - start
            down = (len(data) * 8) / (elapsed * 1024 * 1024)
            return f"Download Speed: {down:.2f} Mbps"
        except Exception as e2:
            return f"Speed test error: {e}"

def execute():
    return run()