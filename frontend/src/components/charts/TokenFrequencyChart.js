import { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function TokenFrequencyChart({ data }) {
  const chartRef = useRef(null);

  useEffect(() => {
    // Exit early if no data 
    if (!data || data.length === 0) return;

    // chart margins and dimensions
    const margin = { top: 30, right: 30, bottom: 120, left: 60 };
    const width = 900 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    // Clear any existing chart elements before redrawing
    d3.select(chartRef.current).selectAll("*").remove();

    //  the main SVG 
    const svg = d3
      .select(chartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // === X-axis setup
    // x0: outer scale for tokens
    const x0 = d3
      .scaleBand()
      .domain(data.map(d => d.token))
      .range([0, width])
      .padding(0.2);

    // x1: inner scale for categories (safe / vulnerable)
    const x1 = d3
      .scaleBand()
      .domain(["safe", "vulnerable"])
      .range([0, x0.bandwidth()])
      .padding(0.05);

    // === Y-axis setup 
    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.safe, d.vulnerable))])
      .nice()
      .range([height, 0]);

    // === Color scale 
    const color = d3
      .scaleOrdinal()
      .domain(["safe", "vulnerable"])
      .range(["#4CAF50", "#D32F2F"]);

    // === Draw grouped bars
    svg
      .append("g")
      .selectAll("g")
      .data(data)
      .enter()
      .append("g")
      .attr("transform", d => `translate(${x0(d.token)},0)`)
      .selectAll("rect")
      .data(d => [
        { key: "safe", value: d.safe },
        { key: "vulnerable", value: d.vulnerable }
      ])
      .enter()
      .append("rect")
      .attr("x", d => x1(d.key))
      .attr("y", d => y(d.value))
      .attr("width", x1.bandwidth())
      .attr("height", d => height - y(d.value))
      .attr("fill", d => color(d.key));

    // === Draw X-axis (tokens) 
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x0))
      .selectAll("text")
      .attr("transform", "rotate(-45)")
      .style("text-anchor", "end")
      .style("font-size", "11px");

    // === Draw Y-axis (frequency scale) 
    svg.append("g").call(d3.axisLeft(y));

    // === Add legend (Safe / Vulnerable)
    const legend = svg.append("g").attr("transform", `translate(${width - 120},0)`);

    ["safe", "vulnerable"].forEach((key, i) => {
      // Color box
      legend
        .append("rect")
        .attr("x", 0)
        .attr("y", i * 22)
        .attr("width", 18)
        .attr("height", 18)
        .attr("fill", color(key));

      // Label text
      legend
        .append("text")
        .attr("x", 25)
        .attr("y", i * 22 + 14)
        .text(key.charAt(0).toUpperCase() + key.slice(1));
    });
  }, [data]);

  // Render the container for the chart
  return <div ref={chartRef}></div>;
}
