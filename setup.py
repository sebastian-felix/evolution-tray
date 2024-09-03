try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# from options["setup"] in build.vel

config = {
    'name': 'evolution-tray',
    'version': '0.1',
    'packages': ['tray'],
    'description': 'A tray icon for Evolution mail client',
    'author': 'Sebastian Felix',
    'url': 'https://github.com/sebastian-felix/evolution-tray',
    'download_url': 'https://github.com/sebastian-felix/evolution-tray',
    'package_data': {"evolution-tray": ["glade/*.glade",
                                    "icons/*.svg",
                                    "ui/*.ui"]},
    'entry_points': {'console_scripts':
                         ['evolution-tray = tray.mail:run']}
}

setup(**config)