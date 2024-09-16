import os

def generate_chord_list(diagram_path):
    chord_list = []

    for root, dirs, files in os.walk(diagram_path):
        for file in files:
            if file.endswith(".png"):
                chord_name = os.path.splitext(file)[0]
                chord_list.append((chord_name, file))

    return chord_list

def generate_html(chord_list, output_file):
    html_content = """<html>
<head>
    <title>Chord List - Guitar </title>
    <link rel="stylesheet" href="./scripts/style.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>All known guitar chords listed</h1>

    <div class="search-container">
        <input type="text" id="chord-search" placeholder="Search by Chord"...">
    </div>

    <ul id="chord-list">
"""

    for chord_name, file_name in chord_list:
        html_content += f"""
        <li class="chord-item" data-chord="{chord_name}">
            <strong>{chord_name}</strong><br>
            <img src='engine/diagrams/guitar/{file_name}' alt='{chord_name} diagram' class="chord-img">
        </li>
"""

    html_content += """    </ul>

<script>
    $(document).ready(function(){
        $('#chord-search').on('keyup', function() {
            var value = $(this).val().toLowerCase();
            $('#chord-list li').filter(function() {
                $(this).toggle($(this).data('chord').toLowerCase().indexOf(value) > -1);
            });
        });
    });
</script>

</body>
</html>"""

    with open(output_file, 'w') as file:
        file.write(html_content)

def main():
    diagram_path = "./engine/diagrams/guitar/"
    output_file = "chord_list.html"

    chord_list = generate_chord_list(diagram_path)
    generate_html(chord_list, output_file)

    print(f"All known chords listed at: {output_file}")

if __name__ == "__main__":
    main()
