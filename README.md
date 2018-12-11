# nethackbot

The virtual screen and the screen parsing routing is taken from the github project WandOfDiscord. The rest is my creation.

This little RL attempt will spawn a nethack game as a male lawful caveman and attempt to learn from it. The wait times are meant to keep the cpu consumptions low and allow it to run in parallel to anything else, since the time taken for this learner to achieve anythink might be significant.


to try it out just run

python3 local.py

in the local directory.

Please do not push the model.keras model to github since it will cause the large file error and you will have it clean it up afterwards
