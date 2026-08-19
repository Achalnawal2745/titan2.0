REQUIREMENTS = ["speedtest-cli"]

def run():
    import speedtest
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download()
    upload_speed = st.upload()
    return f"Download Speed: {download_speed / 1024 / 1024:.2f} Mbps, Upload Speed: {upload_speed / 1024 / 1024:.2f} Mbps"

def test():
    import speedtest
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download()
    assert download_speed > 0
    return True