import { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function HistoryConfidenceChart({ data }) {
  const ref = useRef();

  useEffect(() => {
    // Select SVG and clear previous drawings
    const svg = d3.select(ref.current);
    svg.selectAll("*").remove();

    // Show message if  no data
    if (!Array.isArray(data) || data.length === 0) {
      svg
        .append("text")
        .attr("x", 200)
        .attr("y", 150)
        .attr("text-anchor", "middle")
        .attr("fill", "#aaa")
        .text("No confidence data available");
      return;
    }

    // Parse and clean data
    const parsedData = data
      .filter((d) => d.timestamp && d.confidence !== null)
      .map((d, i) => ({
        id: i,
        timestamp: d3.timeFormat("%Y-%m-%d %H:%M:%S")(new Date(d.timestamp)),
        confidence: +d.confidence,
        result: d.result,
      }));

    // Set chart dimensions and margins
    const width = 900;
    const height = 420;
    const margin = { top: 50, right: 40, bottom: 110, left: 70 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;

    // Create main group element
    const chart = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // X scale (timestamp)
    const xScale = d3
      .scalePoint()
      .domain(parsedData.map((d) => d.timestamp))
      .range([0, innerW])
      .padding(0.5);

    // Y scale (confidence)
    const yScale = d3.scaleLinear().domain([0, 1]).nice().range([innerH, 0]);

    // Draw line
    const line = d3
      .line()
      .x((d) => xScale(d.timestamp))
      .y((d) => yScale(d.confidence))
      .curve(d3.curveMonotoneX);

    chart
      .append("path")
      .datum(parsedData)
      .attr("fill", "none")
      .attr("stroke", "#f3c623")
      .attr("stroke-width", 2)
      .attr("opacity", 0.85)
      .attr("d", line);

    // Create axes
    const xAxis = d3.axisBottom(xScale).tickFormat((d) => d);
    const yAxis = d3.axisLeft(yScale).ticks(6).tickFormat(d3.format(".1f"));

    // Draw X axis
    chart
      .append("g")
      .attr("transform", `translate(0,${innerH})`)
      .call(xAxis)
      .selectAll("text")
      .attr("transform", "rotate(-35)")
      .style("text-anchor", "end")
      .style("fill", "#ccc")
      .style("font-size", "11px");

    // Draw Y axis
    chart.append("g").call(yAxis).selectAll("text").style("fill", "#ccc");

    // Add axis labels
    // X label
    chart
      .append("text")
      .attr("x", innerW / 2)
      .attr("y", innerH + 95)
      .attr("text-anchor", "middle")
      .style("fill", "#ccc")
      .style("font-size", "13px")
      .text("Timestamp (Date + Time)");
    // Y label 
    chart
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerH / 2)
      .attr("y", -50)
      .attr("text-anchor", "middle")
      .style("fill", "#ccc")
      .style("font-size", "13px")
      .text("Confidence Score (0 to 1)");
      //title
    chart
      .append("text")
      .attr("x", innerW / 2)
      .attr("y", -15)
      .attr("text-anchor", "middle")
      .style("fill", "#fff")
      .style("font-weight", "bold")
      .text("Confidence Trend by Timestamp");

    // Tooltip element
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "line-tooltip")
      .style("position", "absolute")
      .style("background", "#222")
      .style("color", "#fff")
      .style("padding", "6px 10px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("opacity", 0)
      .style("pointer-events", "none");

    // Draw dots for each data point
    chart
      .selectAll(".dot")
      .data(parsedData)
      .join("circle")
      .attr("class", "dot")
      .attr("cx", (d) => xScale(d.timestamp))
      .attr("cy", (d) => yScale(d.confidence))
      .attr("r", 5)
      .attr("fill", (d) => (d.result === "Vulnerable" ? "#e74c3c" : "#2ecc71"))
      .attr("opacity", 0.9);
    //============================================================
    // Setting hit zones (=> click areas)
    const hitZones = [];
    const xs = parsedData.map((d) => xScale(d.timestamp));
    const gap = xs.length > 1 ? xs[1] - xs[0] : 50;
    const halfGap = gap / 2;

    for (let i = 0; i < parsedData.length; i++) {
      const current = xScale(parsedData[i].timestamp);
      const prev = xs[i - 1] ?? current - gap;
      const next = xs[i + 1] ?? current + gap;

      let x1, x2;
      if (i === 0) {
        x1 = current - halfGap;
        x2 = (current + next) / 2;
      } else if (i === parsedData.length - 1) {
        x1 = (prev + current) / 2;
        x2 = current + halfGap;
      } else {
        x1 = (prev + current) / 2;
        x2 = (next + current) / 2;
      }
      hitZones.push({ ...parsedData[i], x1, x2 });
    }

    // Draw hit zones (easier hover and click)
    chart
      .selectAll(".hit-zone")
      .data(hitZones)
      .join("rect")
      .attr("class", "hit-zone")
      .attr("x", (d) => Math.max(0, d.x1))
      .attr("width", (d) => Math.min(innerW, d.x2) - Math.max(0, d.x1))
      .attr("y", 0)
      .attr("height", innerH)
      .attr("fill", "transparent")
      .style("cursor", "pointer")
      .on("mouseover", (event, d) => {
        // Highlight area
        d3.select(event.currentTarget)
          .transition()
          .duration(150)
          .attr("fill", "rgba(255, 255, 255, 0.08)");

        // Enlarge selected dot
        d3.selectAll(".dot").attr("r", 5).attr("opacity", 0.8);
        chart
          .selectAll(".dot")
          .filter((p) => p.timestamp === d.timestamp)
          .attr("r", 8)
          .attr("opacity", 1);

        // Show tooltip
        tooltip
          .style("opacity", 1)
          .html(
            `<b>${d.result}</b><br>${d.timestamp}<br>Confidence: ${(d.confidence * 100).toFixed(
              1
            )}%`
          )
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 25}px`);
      })
      .on("mousemove", (event) => {
        tooltip
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 25}px`);
      })
      .on("mouseout", (event) => {
        // Remove highlight and tooltip
        d3.select(event.currentTarget)
          .transition()
          .duration(150)
          .attr("fill", "transparent");
        d3.selectAll(".dot").attr("r", 5).attr("opacity", 0.9);
        tooltip.style("opacity", 0);
      })
      .on("click", (_, d) => {
        // Scroll to the corresponding record card
        const target = document.getElementById(`history-${d.id}`);//I will set in HistoryPage.js
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "center" });
          target.style.transition = "background-color 0.8s ease";
          target.style.backgroundColor = "#444";
          setTimeout(() => (target.style.backgroundColor = ""), 800);
        }
      });
  }, [data]);

  // Return chart container
  return (
    <svg
      ref={ref}
      style={{
        width: "100%",
        height: 420,
        display: "block",
      }}
    />
  );
}
