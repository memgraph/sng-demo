(async() => {
    let response = await fetch(`${window.origin}/get-graph`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify("Get data"),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    });

    var width = 960,
        height = 600

    var svg = d3.select("svg").append("svg")
        .attr("width", width)
        .attr("height", height);

    var force = d3.layout.force()
        .gravity(.05)
        .charge(-240)
        .linkDistance(150)
        .size([width, height]);

    let responseString = await response.json();
    let responseJSON = JSON.parse(responseString);

    var nodeById = d3.map();

    responseJSON.nodes.forEach(function(node) {
        nodeById.set(node.id, node);
    });

    responseJSON.edges.forEach(function(link) {
        link.source = nodeById.get(link.source);
        link.target = nodeById.get(link.target);
    });

    force
        .nodes(responseJSON.nodes)
        .links(responseJSON.edges)
        .start();

    var node = svg.selectAll(".node")
        .data(responseJSON.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

    var link = svg.selectAll(".link")
        .data(responseJSON.edges)
        .enter().append("line")
        .attr("class", "link")
        .attr("stroke-width", "1px");

    node.append("circle")
        .attr("r", "30")
        .style("fill", "lightgray")
        .style("stroke", "black")
        .style("stroke-width", "1px");

    node.append("text")
        .style("text-anchor", "middle")
        .attr("y", 15)
        .text(function(d) {
            return d.name
        });

    force.on("tick", function() {
        link.attr("x1", function(d) {
                return d.source.x;
            })
            .attr("y1", function(d) {
                return d.source.y;
            })
            .attr("x2", function(d) {
                return d.target.x;
            })
            .attr("y2", function(d) {
                return d.target.y;
            });

        node.attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        });
    });
})();