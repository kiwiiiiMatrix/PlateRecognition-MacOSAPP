from setuptools import setup

OPTIONS = {
    'plist': {
        'NSCameraUsageDescription': '我们需要访问您的摄像头以进行车牌识别。'
    }
}

setup(
    app=['design_system_rc.py'],
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)