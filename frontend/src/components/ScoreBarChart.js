import { useRef, useEffect, useState } from "react";
import * as d3 from "d3";

function ScoreBarChart({ data }) {
  const ref = useRef();
  const [selectedLine, setSelectedLine] = useState(null); // Track selected bar

  useEffect(() => {
    // Reset selected line when new data arrives
    setSelectedLine(null);

    // Initialize SVG
    const svgBar = d3.select(ref.current);
    svgBar.selectAll("*").remove();

    // Handle empty dataset
    if (!data || data.length === 0) {
      const width = svgBar.node()?.clientWidth || 600;
      const height = 300;
      const margin = { top: 30, right: 30, bottom: 50, left: 60 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;

      const svg = svgBar
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

      // Empty axes
      const x = d3.scaleBand().domain([]).range([0, innerW]);
      const y = d3.scaleLinear().domain([0, 1]).range([innerH, 0]);

      svg
        .append("g")
        .attr("transform", `translate(0, ${innerH})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("fill", "#777");

      svg.append("g").call(d3.axisLeft(y).ticks(5)).selectAll("text").style("fill", "#777");

      // Message for empty state
      svg
        .append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#ccc")
        .text("No vulnerable lines to display.");

      return;
    }

    // Draw chart if data exists
    drawChart(data);

    // Cleanup tooltips
    return () => {
      d3.selectAll(".vuln-tooltip").remove();
    };
  }, [data]);
  //==================================================================
  const drawChart = (data) => {
    const svgBar = d3.select(ref.current);
    svgBar.selectAll("*").remove();

    // Chart dimensions
    const width = svgBar.node().clientWidth || 800;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 60, left: 60 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    const svg = svgBar
      .attr("width", width)
      .attr("height", height)
      .style("background", "transparent")
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // X axis (line numbers)
    const x = d3
      .scaleBand()
      .domain(data.map((d) => String(d.line)))
      .range([0, innerW])
      .padding(0.25);

    // Y axis (vulnerability scores)
    const maxScore = d3.max(data, (d) => d.score) || 0.1;
    const y = d3
      .scaleLinear()
      .domain([0, Math.max(0.1, maxScore)])
      .nice()
      .range([innerH, 0]);

    // Color scale
    const color = d3.scaleSequential(d3.interpolateReds).domain([0, 1]);

    // Tooltip setup
    const tooltip = d3
      .select("body")
      .selectAll(".vuln-tooltip")
      .data([0])
      .join("div")
      .attr("class", "vuln-tooltip")
      .style("position", "absolute")
      .style("background", "rgba(30,30,30,0.9)")
      .style("color", "#fff")
      .style("padding", "6px 10px")
      .style("border-radius", "6px")
      .style("font-size", "13px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    // Draw bars
    const bars = svg
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => x(String(d.line)))
      .attr("width", x.bandwidth())
      .attr("y", innerH)
      .attr("height", 0)
      .attr("fill", (d) => color(d.score))
      .style("cursor", "pointer");

    // Hover interaction
    bars
      .on("mousemove", function (event, d) {
        svg.selectAll("rect").attr("fill", (b) => color(b.score));
        d3.select(this).attr("fill", "#ff7675").attr("opacity", 0.9);
        tooltip
          .style("opacity", 1)
          .html(`Line ${d.line}<br/>Score: ${(d.score * 100).toFixed(1)}%`)
          .style("left", event.pageX + 12 + "px")
          .style("top", event.pageY - 28 + "px");
      })
      .on("mouseout", function () {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("fill", (d) => color(d.score))
          .attr("opacity", 1);
        tooltip.transition().duration(150).style("opacity", 0);
      })
      .on("click", function (event, d) {
        // Select or deselect a bar
        setSelectedLine((prev) => (prev && prev.line === d.line ? null : d));
      });

    // Animate bars on load
    bars
      .transition()
      .duration(700)
      .delay((_, i) => i * 40)
      .attr("y", (d) => y(d.score))
      .attr("height", (d) => innerH - y(d.score));

    // Numeric labels on top
    svg
      .selectAll(".bar-label")
      .data(data)
      .join("text")
      .attr("class", "bar-label")
      .attr("x", (d) => x(String(d.line)) + x.bandwidth() / 2)
      .attr("y", (d) => y(d.score) - 5)
      .attr("text-anchor", "middle")
      .style("fill", "#eee")
      .style("font-size", "11px")
      .text((d) => `${(d.score * 100).toFixed(1)}%`);

    // X axis
    svg
      .append("g")
      .attr("transform", `translate(0, ${innerH})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("fill", "#ccc")
      .style("font-size", "13px")
      .style("font-weight", "600")
      .attr("dy", "1.5em");

    // Y axis
    svg
      .append("g")
      .call(d3.axisLeft(y).ticks(5))
      .selectAll("text")
      .style("fill", "#ccc")
      .style("font-size", "12px");

    // Chart title
    svg
      .append("text")
      .attr("x", innerW / 2)
      .attr("y", -10)
      .attr("text-anchor", "middle")
      .style("font-weight", "bold")
      .style("fill", "#fff")
      .text("Vulnerable Line Scores");

    // X axis label
    svg
      .append("text")
      .attr("x", innerW / 2)
      .attr("y", innerH + 50)
      .attr("text-anchor", "middle")
      .style("fill", "#ccc")
      .style("font-size", "14px")
      .style("font-weight", "700")
      .text("Line Number");

    // Y axis label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerH / 2)
      .attr("y", -45)
      .attr("text-anchor", "middle")
      .style("fill", "#ccc")
      .style("font-size", "14px")
      .style("font-weight", "700")
      .text("Vulnerability Score");
  };

  // Render SVG and detail panel
  return (
    <div>
      <svg
        ref={ref}
        style={{
          width: "100%",
          height: 300,
          display: "block",
        }}
      />
      {/* Detail panel for selected line */}
      {selectedLine && (
        <div
          style={{
            background: "#1e1e1e",
            color: "#fff",
            padding: "10px 15px",
            borderRadius: "8px",
            marginTop: "10px",
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          <strong>Line {selectedLine.line}</strong> —{" "}
          <span style={{ color: "#ccc" }}>
            Score: {(selectedLine.score * 100).toFixed(1)}%
          </span>
          <pre style={{ marginTop: "8px", color: "#9cdcfe" }}>
            {selectedLine.snippet}
          </pre>
        </div>
      )}
    </div>
  );
}

export default ScoreBarChart;
