// D3.js visualization components for Tío Pepe dashboard

class VisualizationManager {
    constructor() {
        this.chartTypes = {
            lineChart: this.createLineChart,
            barChart: this.createBarChart,
            pieChart: this.createPieChart,
            heatmap: this.createHeatmap
        };
    }

    async initializeVisualization(container, type, dataSource) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const data = await this.fetchData(dataSource);
        if (this.chartTypes[type]) {
            this.chartTypes[type].call(this, svg, data, width, height);
        }
    }

    async fetchData(dataSource) {
        try {
            const response = await fetch(`/api/dashboard/data/${dataSource}`);
            if (!response.ok) throw new Error('Data fetch failed');
            return await response.json();
        } catch (error) {
            console.error('Error fetching data:', error);
            return this.generateSampleData(dataSource);
        }
    }

    generateSampleData(dataSource) {
        switch(dataSource) {
            case 'systemMetrics':
                return Array.from({length: 24}, (_, i) => ({
                    time: i,
                    value: Math.random() * 100,
                    metric: 'CPU Usage'
                }));
            case 'taskActivity':
                return Array.from({length: 10}, (_, i) => ({
                    category: `Task ${i}`,
                    value: Math.random() * 100,
                    status: Math.random() > 0.5 ? 'completed' : 'pending'
                }));
            case 'agentPerformance':
                return Array.from({length: 5}, (_, i) => ({
                    agent: `Agent ${i}`,
                    performance: Math.random() * 100,
                    tasks: Math.floor(Math.random() * 50)
                }));
            default:
                return [];
        }
    }

    createLineChart(svg, data, width, height) {
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const x = d3.scaleLinear()
            .domain([0, data.length - 1])
            .range([0, innerWidth]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)])
            .range([innerHeight, 0]);

        const line = d3.line()
            .x(d => x(d.time))
            .y(d => y(d.value));

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        g.append('path')
            .datum(data)
            .attr('class', 'line')
            .attr('fill', 'none')
            .attr('stroke', 'steelblue')
            .attr('stroke-width', 1.5)
            .attr('d', line);

        g.append('g')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(d3.axisBottom(x));

        g.append('g')
            .call(d3.axisLeft(y));

        // Add tooltips
        const tooltip = d3.select(svg.node().parentNode)
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        g.selectAll('.dot')
            .data(data)
            .enter().append('circle')
            .attr('class', 'dot')
            .attr('cx', d => x(d.time))
            .attr('cy', d => y(d.value))
            .attr('r', 3.5)
            .on('mouseover', (event, d) => {
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                tooltip.html(`Time: ${d.time}<br/>Value: ${d.value.toFixed(2)}`)
                    .style('left', (event.pageX + 5) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });
    }

    createBarChart(svg, data, width, height) {
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const x = d3.scaleBand()
            .domain(data.map(d => d.category))
            .range([0, innerWidth])
            .padding(0.1);

        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)])
            .range([innerHeight, 0]);

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        g.selectAll('.bar')
            .data(data)
            .enter().append('rect')
            .attr('class', 'bar')
            .attr('x', d => x(d.category))
            .attr('y', d => y(d.value))
            .attr('width', x.bandwidth())
            .attr('height', d => innerHeight - y(d.value))
            .attr('fill', 'steelblue');

        g.append('g')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(d3.axisBottom(x));

        g.append('g')
            .call(d3.axisLeft(y));
    }

    createPieChart(svg, data, width, height) {
        const radius = Math.min(width, height) / 2;
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        const pie = d3.pie()
            .value(d => d.value);

        const arc = d3.arc()
            .innerRadius(0)
            .outerRadius(radius - 10);

        const g = svg.append('g')
            .attr('transform', `translate(${width/2},${height/2})`);

        const arcs = g.selectAll('.arc')
            .data(pie(data))
            .enter().append('g')
            .attr('class', 'arc');

        arcs.append('path')
            .attr('d', arc)
            .style('fill', d => color(d.data.category));

        arcs.append('text')
            .attr('transform', d => `translate(${arc.centroid(d)})`)
            .attr('dy', '.35em')
            .text(d => d.data.category);
    }

    createHeatmap(svg, data, width, height) {
        const margin = {top: 20, right: 20, bottom: 30, left: 40};
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Transform data into a matrix format
        const matrix = this.transformToMatrix(data);

        const x = d3.scaleBand()
            .domain(d3.range(matrix[0].length))
            .range([0, innerWidth])
            .padding(0.1);

        const y = d3.scaleBand()
            .domain(d3.range(matrix.length))
            .range([0, innerHeight])
            .padding(0.1);

        const color = d3.scaleSequential()
            .interpolator(d3.interpolateYlOrRd)
            .domain([0, d3.max(matrix.flat())]);

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        g.selectAll('g')
            .data(matrix)
            .enter().append('g')
            .attr('transform', (d, i) => `translate(0,${y(i)})`)
            .selectAll('rect')
            .data(d => d)
            .enter().append('rect')
            .attr('x', (d, i) => x(i))
            .attr('width', x.bandwidth())
            .attr('height', y.bandwidth())
            .style('fill', d => color(d));
    }

    transformToMatrix(data) {
        // Example transformation - should be adapted based on actual data structure
        const size = Math.ceil(Math.sqrt(data.length));
        const matrix = Array(size).fill().map(() => Array(size).fill(0));
        data.forEach((d, i) => {
            const row = Math.floor(i / size);
            const col = i % size;
            matrix[row][col] = d.value;
        });
        return matrix;
    }
}

// Export the visualization manager
window.VisualizationManager = VisualizationManager;