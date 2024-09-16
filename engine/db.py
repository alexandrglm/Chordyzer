import json
import os
import re
from collections import defaultdict
from datetime import datetime

DB_FILE = "chords_db.json"

def generate_db_html():
    if os.path.exists(DB_FILE):
        created_at = datetime.fromtimestamp(os.path.getctime(DB_FILE)).strftime("%Y-%m-%d %H:%M:%S")
        updated_at = datetime.fromtimestamp(os.path.getmtime(DB_FILE)).strftime("%Y-%m-%d %H:%M:%S")
        with open(DB_FILE, "r", encoding="utf-8") as f:
            chords_db = json.load(f)
    else:
        created_at = "Unknown"
        updated_at = "Unknown"
        chords_db = []

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="icon" href="./favicon.ico" sizes="any">
        <link rel="icon" href="./favicon.svg" type="image/svg+xml">
        <meta charset="UTF-8">
        <title>MUSIC DATABASE</title>
        <script src="./engine/scripts/chart.js"></script>
        <script src="./engine/scripts/jquery.min.js"></script>
        <script src="./engine/scripts/jquery.dataTables.min.js"></script>
        <link rel="stylesheet" href="./engine/scripts/jquery.dataTables.min.css">
        <link rel="stylesheet" href="./engine/scripts/style.css">
        <style>
            #buttons {{
                margin-bottom: 20px;
            }}

            #buttons button {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }}

            #buttons button:hover {{
                background-color: #45a049;
            }}

            #table-container {{
                margin-top: 20px;
            }}

            table {{
                width: 100%;
                margin-top: 20px;
                border-collapse: collapse;
                background-color: #f4f4f4;
            }}

            table, th, td {{
                border: 1px solid #ddd;
            }}

            th, td {{
                padding: 12px;
                text-align: center;
                position: relative;
            }}

            th {{
                background-color: #4CAF50;
                color: white;
            }}

            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}

            tr:hover {{
                background-color: #ddd;
            }}

            .chord-image {{
                display: none;
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10;
                width: 150px;
                border: 1px solid #ddd;
                background: #fff;
                padding: 5px;
            }}

            td:hover .chord-image {{
                display: block;
            }}

            canvas {{
                display: block;
                margin: 20px auto;
            }}
        </style>
    </head>
    <body>
    <h1>Chords Database</h1>
    <p>Created at: {created_at}</p>
    <p>Last updated: {updated_at}</p>
    <div id="buttons">
        <button onclick="showTable()">Table Database</button>
        <button onclick="showBarChart()">Bar Graphs</button>
        <button onclick="showLineChart()">Line Graphs</button>
        <button onclick="showPieChart()">Pie Chart</button>
    </div>
    <div id="table-container">
        <table id="chords-table" class="display">
            <thead>
                <tr>
                    <th>Artist</th>
                    <th>Title</th>
                    <th>Chord</th>
                    <th>Times used</th>
                    <th>BPM</th>
                    <th>Keynote</th>
                </tr>
            </thead>
            <tbody>
    """

    chord_counts = defaultdict(int)

    for entry in chords_db:
        artist = entry.get("artist", "Unknown")
        title = entry.get("title", "Unknown")
        bpm = entry.get("bpm", "N/A")
        keynote = entry.get("keynote", {})

        best_keynote = max(keynote, key=keynote.get, default="Unknown")

        for chord_change in entry.get("chords", {}):
            if isinstance(chord_change, str):
                match = re.search(r"chord='(.+?)', timestamp=(\d+\.\d+)", chord_change)
                if match:
                    chord = match.group(1)
                else:
                    chord = "N/A"
            elif isinstance(chord_change, dict):
                chord = chord_change.get("chord", "N/A")
            else:
                chord = "N/A"

            if chord == "N":
                continue

            chord_counts[(artist, title, chord, bpm, best_keynote)] += 1

    for (artist, title, chord, bpm, keynote), count in chord_counts.items():
        chord_image = f"./engine/diagrams/guitar/{chord}.png"
        html_content += f"""
            <tr>
                <td>{artist}</td>
                <td>{title}</td>
                <td>
                    {chord}
                    <img src="{chord_image}" alt="Diagram of {chord}" class="chord-image">
                </td>
                <td>{count}</td>
                <td>{bpm}</td>
                <td>{keynote}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
    </div>

    <canvas id="chart-canvas" width="400" height="200" style="display:none;"></canvas>

    <script>
        var chart;

        function destroyChart() {
            if (chart) {
                chart.destroy();
            }
        }

        function showTable() {
            document.getElementById("table-container").style.display = "block";
            document.getElementById("chart-canvas").style.display = "none";
        }

        function showBarChart() {
            document.getElementById("table-container").style.display = "none";
            document.getElementById("chart-canvas").style.display = "block";
            destroyChart();
            chart = new Chart(document.getElementById("chart-canvas"), {
                type: 'bar',
                data: getDataForChart(),
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Bar Graph of Chords Used'
                        }
                    }
                }
            });
        }

        function showLineChart() {
            document.getElementById("table-container").style.display = "none";
            document.getElementById("chart-canvas").style.display = "block";
            destroyChart();
            chart = new Chart(document.getElementById("chart-canvas"), {
                type: 'line',
                data: getDataForChart(),
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Line Graph of Chords Used'
                        }
                    }
                }
            });
        }

        function showPieChart() {
            document.getElementById("table-container").style.display = "none";
            document.getElementById("chart-canvas").style.display = "block";
            destroyChart();
            chart = new Chart(document.getElementById("chart-canvas"), {
                type: 'pie',
                data: getDataForChart(),
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Pie Chart of Chords Distribution'
                        }
                    }
                }
            });
        }

        function getDataForChart() {
            var labels = [];
            var data = [];

            $('#chords-table tbody tr').each(function() {
                var artist = $(this).find('td').eq(0).text();
                var title = $(this).find('td').eq(1).text();
                var chord = $(this).find('td').eq(2).text();
                var timesUsed = parseInt($(this).find('td').eq(3).text());
                labels.push(artist + " - " + title + " (" + chord + ")");
                data.push(timesUsed);
            });

            return {
                labels: labels,
                datasets: [{
                    label: 'Times Used',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            };
        }

        $(document).ready(function() {
            $('#chords-table').DataTable({
                "paging": true,
                "lengthChange": true,
                "searching": true,
                "ordering": true,
                "info": true,
                "autoWidth": false,
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/1.10.21/i18n/Spanish.json"
                }
            });
        });
    </script>
    </body>
    </html>
    """

    db_html_file = "chords_database.html"
    with open(db_html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML file generated: {db_html_file}")
    return db_html_file
