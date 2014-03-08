
function Sun_Burst(width_, height_, b_, colors_, uid){
    this.totalSize = 0
    this.width = width_;
    this.height = height_;
    this.radius = Math.min(this.width, this.height) / 2;
    this.b = b_;
    this.colors = colors_;
    this.uid = uid;
    this.entries = {};
    this.seq = "#sequence_" + this.uid;
    this.trailid = "#trail_" + this.uid;
    this.elbl = "#endlabel_" + this.uid;
    this.bwidth = this.width
    this.partition = d3.layout.partition()
	.size([2 * Math.PI, this.radius * this.radius])
	.value(function(d) { return d.size; });

    this.arc = d3.svg.arc()
	.startAngle(function(d) { return d.x; })
	.endAngle(function(d) { return d.x + d.dx; })
	.innerRadius(function(d) { return Math.sqrt(d.y); })
	.outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });

    this.vis = d3.select("#chart_" + this.uid).append("svg:svg")
	.attr("width", this.width)
	.attr("height", this.height)
	.append("svg:g")
	.attr("id", "container_" + this.uid)
	.attr("transform", "translate(" + this.width / 2 + "," + this.height / 2 + ")")
	

}


// Given a node in a partition layout, return an array of all of its ancestor
// nodes, highest first, but excluding the root.
Sun_Burst.prototype = {

    setBreadWidth : function(s, w){this.seq = s; this.bwidth = w;},

    getAncestors: function(node){
	var path = [],  current = node;
	while (current.parent) {
	    path.unshift(current);
	    current = current.parent;
	}
	return path;
    },

    // Dimensions of legend item: width, height, spacing, radius of rounded rect.
    //li = {w: 190, h: 30, s: 3, r: 3};
    createVisualization:function(json, li) {
	var nodes, path, that = this; 
	// according to george, JS is wierd, in that, the keyword this, changes.  as a result, in a callback, 'this' doesn't mean
	// the parent class, but the object the callback is called from.  To work around this, he said people will use var that = this;
	// and define the function within the same closure, while using the 'that' variable while construction the callback function.
	this.mouseover = function(d) {
	    
	    var percentageString, sequenceArray;
	    percentageString = that.makePctStr(d.value, that.totalSize);
	    d3.select("#percentage_" + that.uid).text(percentageString);
	    d3.select("#explanation_" + that.uid).style("visibility", "");
	    
	    sequenceArray = that.getAncestors(d);
	    that.updateBreadcrumbs(sequenceArray, percentageString);
	    d3.select("#chart_"+that.uid).selectAll("path").style("opacity", 0.3);
	    that.vis.selectAll("path").filter(function(node) {return (sequenceArray.indexOf(node) >= 0)	}).style("opacity", 1);
	};

	this.mouseleave = function(d) {
	    d3.select("#trail_" + that.uid).style("visibility", "hidden");
	    d3.select("#chart_"+ that.uid).selectAll("path").on("mouseover", null);
	    d3.select("#chart_"+ that.uid).selectAll("path")
		.transition().duration(1000).style("opacity", 1)
		.each("end", function() { d3.select(this).on("mouseover", that.mouseover); });
	    d3.select("#explanation_" + that.uid).transition().duration(1000).style("visibility", "hidden");
	};
	
	this.initializeBreadcrumbTrail();
	this.vis.append("svg:circle").attr("r", this.radius).style("opacity", 0);
	// DLS - commented sicne we want to show all.. maybe we need to look into how to zoom
	//nodes = this.partition.nodes(json).filter(function(d) {return (d.dx > 0.005);}); // 0.005 radians = 0.29 degrees

	nodes = this.partition.nodes(json);
	path = this.vis.data([json]).selectAll("path")
	    .data(nodes)
	    .enter().append("svg:path")
	    .attr("display", function(d) { return d.depth ? null : "none"; })
	    .attr("d", this.arc)
	    .attr("fill-rule", "evenodd")
	    .style("fill", function(d) { return d.color; })
	    .style("opacity", 1)
	    .on("mouseover", this.mouseover);

	d3.select("#container_" + this.uid).on("mouseleave", this.mouseleave);
	this.totalSize = path.node().__data__.value;

	// go through each child and determine their size vs. the total
	for (var itm in path.node().__data__.children){
	    itm = path.node().__data__.children[itm];
	    this.entries[itm.name] = itm.name + " - " + this.makePctStr(itm.value, this.totalSize);	    
	}
	this.drawLegend(li);
    },

    makePctStr : function(cnt, total){
	var percentage = (100 * cnt / total).toPrecision(3);
	var percentageString = percentage + "%";
	if (percentage < 0.1) {
	    percentageString = "< 0.1%";
	}
	return percentageString;
    },

    initializeBreadcrumbTrail : function() {
	// Add the svg area.
	var trail = d3.select(this.seq).append("svg:svg")
	    .attr("width", this.bwidth)
	    .attr("height", 50)
	    .attr("id", "trail_" + this.uid);
	// Add the label at the end, for the percentage.
	trail.append("svg:text")
	    .attr("id", this.elbl)
	    .style("fill", "#000");
    },

    updateBreadcrumbs : function(nodeArray, percentageString) {
	var g, entering;
	// Data join; key function combines name and depth (= position in sequence).
	g = d3.select(this.trailid)
	    .selectAll("g")
	    .data(nodeArray, function(d) { return d.name + d.depth; });
	
	// Add breadcrumb and label for entering nodes.
	entering = g.enter().append("svg:g");
	var that = this;

	var breadcrumbPoints = function(d, i) {
	    var points = [];
	    points.push("0,0");
	    points.push(that.b.w + ",0");
	    points.push(that.b.w + that.b.t + "," + (that.b.h / 2));
	    points.push(that.b.w + "," + that.b.h);
	    points.push("0," + that.b.h);
	    if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
		points.push(that.b.t + "," + (that.b.h / 2));
	    }
	    return points.join(" ");
	}
	
	entering.append("svg:polygon")
	    .attr("points", breadcrumbPoints)
	    .style("fill", function(d) { return d.color; });
	
	entering.append("svg:text")
	    .attr("x", (this.b.w + this.b.t) / 2)
	    .attr("y", this.b.h / 2)
	    .attr("dy", "0.35em")
	    .attr("text-anchor", "middle")
	    .text(function(d) { return d.name; });
	// Set position for entering and updating nodes.
	g.attr("transform", function(d, i) {return "translate(" + i * (that.b.w + that.b.s) + ", 0)";});
	
	// Remove exiting nodes.
	g.exit().remove();
	
	// Now move and update the percentage at the end.
	d3.select(this.trailid).select(this.elbl)
	    .attr("x", (nodeArray.length + 0.5) * (this.b.w + this.b.s))
	    .attr("y", this.b.h / 2)
	    .attr("dy", "0.35em")
	    .attr("text-anchor", "middle")
	    .text(percentageString);
	
	// Make the breadcrumb trail visible, if it's hidden.
	d3.select(this.trailid).style("visibility", "");
	
    },

    drawLegend : function(li) {
	var legend, g

	legend = d3.select("#legend_" + this.uid).append("svg:svg")
	    .attr("width", li.w)
	    .attr("height", d3.keys(this.colors).length * (li.h + li.s));

	g = legend.selectAll("g")
	    .data(d3.entries(this.colors))
	    .enter().append("svg:g")
	    .attr("transform", function(d, i) {
		return "translate(0," + i * (li.h + li.s) + ")";
            });
	
	g.append("svg:rect")
	    .attr("rx", li.r)
	    .attr("ry", li.r)
	    .attr("width", li.w)
	    .attr("height", li.h)
	    .style("fill", function(d) { return d.value; });
	
	var that = this;
	g.append("svg:text")
	    .attr("x", li.w / 2)
	    .attr("y", li.h / 2)
	    .attr("dy", "0.35em")
	    .attr("text-anchor", "middle")
	    .text(function(d) {return that.entries[d.key]; });
    },
};
