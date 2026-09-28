import platform
import subprocess


def check_internet_connection(ip: str = "8.8.8.8", timeout: float = 2.0) -> bool:
    assert platform.system().lower() != "windows", "Windows is not and will never be supported"

    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(int(timeout)), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 1,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False

    return result.returncode == 0
