import  { useRef, useEffect } from "react";
import * as d3 from "d3";

// This draws a bar chart for line level vulnerability scores.

function ScoreBarChart({ data }) {
  const ref = useRef();

  useEffect(() => {
    // Select SVG and clear previous content
    const svgBar = d3.select(ref.current);
    svgBar.selectAll("*").remove();

    // Show message when no data
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

      // Message for empty data
      svg
        .append("text")
        .attr("x", innerW / 2)
        .attr("y", innerH / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#ccc")
        .text("No vulnerable lines to display.");

      return;
    }

    // Draw chart when data exists
    drawChart(data);
  }, [data]);

  const drawChart = (data) => {
    // Select SVG and clear
    const svgBar = d3.select(ref.current);
    svgBar.selectAll("*").remove();

    // Set up dimensions
    const width = svgBar.node().clientWidth || 800;
    const height = 300;
    const margin = { top: 30, right: 30, bottom: 50, left: 60 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    // Create main group
    const svg = svgBar
      .attr("width", width)
      .attr("height", height)
      .style("background", "transparent")
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    // X scale (line numbers)
    const x = d3
      .scaleBand()
      .domain(data.map((d) => String(d.line)))
      .range([0, innerW])
      .padding(0.2);

    // Y scale (score values)
    const maxScore = d3.max(data, (d) => d.score) || 0.1;
    const y = d3
      .scaleLinear()
      .domain([0, Math.max(0.1, maxScore)])
      .nice()
      .range([innerH, 0]);

    // Color scale (red gradient)
    const color = d3.scaleSequential(d3.interpolateReds).domain([0, 1]);

    // Tooltip box
    const tooltip = d3
      .select("body")
      .selectAll(".vuln-tooltip")
      .data([0])
      .join("div")
      .attr("class", "vuln-tooltip")
      .style("position", "absolute")
      .style("background", "#333")
      .style("color", "#fff")
      .style("padding", "6px 10px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    // Draw bars
    svg
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => x(String(d.line)))
      .attr("width", x.bandwidth())
      .attr("y", innerH)
      .attr("height", 0)
      .attr("fill", (d) => color(d.score))
      // Mouse events for tooltip
      .on("mouseover", (event, d) => {
        tooltip
          .style("opacity", 1)
          .html(
            `Line ${d.line}<br/>Score: ${(d.score * 100).toFixed(1)}%<br/>${d.snippet}`
          )
          .style("left", event.pageX + 10 + "px")
          .style("top", event.pageY - 20 + "px");
      })
      .on("mousemove", (event) => {
        tooltip
          .style("left", event.pageX + 10 + "px")
          .style("top", event.pageY - 20 + "px");
      })
      .on("mouseout", () => tooltip.style("opacity", 0))
      // Bar animation
      .transition()
      .duration(700)
      .attr("y", (d) => y(d.score))
      .attr("height", (d) => innerH - y(d.score));

    // Draw X axis
    svg
      .append("g")
      .attr("transform", `translate(0, ${innerH})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("fill", "#ccc");

    // Draw Y axis
    svg.append("g").call(d3.axisLeft(y).ticks(5)).selectAll("text").style("fill", "#ccc");

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
      .attr("y", innerH + 40)
      .attr("text-anchor", "middle")
      .style("fill", "#ccc")
      .style("font-size", "12px")
      .text("Line Number");

    // Y axis label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerH / 2)
      .attr("y", -45)
      .attr("text-anchor", "middle")
      .style("fill", "#ccc")
      .style("font-size", "12px")
      .text("Vulnerability Score");
  };

  // Return SVG element
  return (
    <svg
      ref={ref}
      style={{
        width: "100%",
        height: 300,
        display: "block",
      }}
    />
  );
}

export default ScoreBarChart;
