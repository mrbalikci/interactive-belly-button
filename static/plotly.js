// Create a function to append a table and 
// run the plots and charts 

function appendTable(name) {
    // extentions of the urls from app.py
    var url_samples = '/samples/' + name;
    var url_meta = "/metadata/" + name;

    // print it on console 
    console.log(url_meta)
    console.log(url_samples)

    // append the metadata to the table 
    Plotly.d3.json(url_meta, function (error, response) {
        console.log(response);

        Plotly.d3.select("tbody")
            .html("")
            .selectAll("tr")
            .data(response)
            .enter()
            .append("tr")
            .html(function (d) {
                return `<td>${d.t0}</td><td>${d.t1}</td>`
            })
    })

    // plot the pie chart 
    Plotly.d3.json(url_samples, function (error, pieData) {

        // define the veriables and data and layout for plotly
        var otu_label = pieData['otu_id']
        var otu_value = pieData['sample_values']

        var data = [{
            values: otu_value,
            labels: otu_label,
            type: "pie"
        }];

        var layout = {
            title: 'Sample Value Pie Chart',
            height: 500,
            width: 700
        };

        Plotly.newPlot("plotPie", data, layout);
    });

    // make the bubble plot 
    Plotly.d3.json(url_samples, function (error, bubbleData) {

        // define the veriables and data and layout 
        var x_values = bubbleData["otu_id"]
        var y_values = bubbleData["sample_values"]

        var data = [{
            x: x_values,
            y: y_values,
            mode: 'markers',
            marker: {
                size: y_values,
                color: x_values
            },
        }]

        var layout = {
            title: 'OTU IDs vs Sample Values',
            height: 700,
            width: 1200,
            xaxis: {
                title: 'OTU ID',
                showgrid: false,
                zeroline: false
            },
            yaxis: {
                title: 'Sample Values',
                showline: false
            }
        }

        Plotly.newPlot("plotBubble", data, layout)
    });
}

// functions for the names that will appear in the 
// select section in HTML 
var url = "/names";
function init() {
    Plotly.d3.json(url, function (error, names) {


        var select = Plotly.d3.select('#selDataset')
            .on("change", function () {
                var name = Plotly.d3.select(this).node().value;

                appendTable(name);
            });
        select.selectAll('option')
            .data(names)
            .enter()
            .append('option')

            .text(d => d)
            .attr("value", function (d) { return d; })
    });
}

// run the function 
init();