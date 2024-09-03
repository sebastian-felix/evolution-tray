try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# from options["setup"] in build.vel

config = {
    'name': 'evolution-tray',
    'version': '0.1',
    'packages': ['tray'],
    'description': 'snapper-gui graphical user interface for snapper btrfs snapshot manager',
    'author': 'Ricardo Vieira',
    'url': 'https://github.com/ricardo-vieira/snapper-gui',
    'download_url': 'https://github.com/ricardo-vieira/snapper-gui',
    'author_email': 'ricardo.vieira@ist.utl.pt',
    'package_data': {"evolution-tray": ["glade/*.glade",
                                    "icons/*.svg",
                                    "ui/*.ui"]},
    'entry_points': {'console_scripts':
                         ['evolution-tray = tray.mail:run']}
}

setup(**config)