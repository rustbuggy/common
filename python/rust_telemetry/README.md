# Libraries

## Mac OS X
    brew tap Homebrew/python
    brew update
    brew install pygame

Try if pygame is found
    python
    import pygame

If moudule is not found check where homewbrew installed it
    brew info pygame

Lets say it was in "/usr/local/Cellar/pygame/1.9.1release", add this to .profile
    export PYTHONPATH=/usr/local/Cellar/pygame/1.9.1release:$PYTHONPATH
