def process_file(input_filename, output_filename):
    with open(input_filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    
    with open(output_filename, "w", encoding="utf-8") as outfile:
        for line in lines:
            count_ampersands = line.count("&")
            if count_ampersands >= 5:
                line = line[::-1].replace("&", "@", 4)[::-1]  # Zamenjamo zadnje 4 & v vrstici
            else:
                line = line.replace("&", "@")  # Zamenjamo vse &
            outfile.write(line)

# Primer uporabe
process_file("data/podatki.txt", "data/podatki2.txt")
