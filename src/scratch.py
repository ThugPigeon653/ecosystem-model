import subprocess
import os
import re

with open("trace.txt", "r") as input_file:
    content = input_file.read()
    spaces = True
    while spaces:
        cache_content = content
        content = content.replace("  ", " ")
        if content == cache_content:
            spaces = False

with open("cleaned_trace.txt", "w") as output_file:
    output_file.write(content)

print("Data cleaned and saved as cleaned_trace.txt")
