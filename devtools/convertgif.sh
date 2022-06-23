ffmpeg -i cfscripts_tmp.gif -ss 00:00:01.5 -t 00:00:15.5 -vf "fps=16,scale=1500:-2:flags=lanczos,split[s0][s1];\
[s0]palettegen=max_colors=128:reserve_transparent=0[p];\
[s1][p]paletteuse" -async 1 cfscripts_final.gif
