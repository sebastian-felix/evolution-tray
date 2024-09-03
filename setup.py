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
    'package_data': {"evolution-tay": ["glade/*.glade",
                                    "icons/*.svg",
                                    "ui/*.ui"]},
    'data_files': [('share/applications', ['snapper-gui.desktop'])],
    'entry_points': {'console_scripts':
                         ['evolution-tray = tray.mail-unread:run']}
}

setup(**config)