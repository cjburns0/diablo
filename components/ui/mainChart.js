/**
 * Main Chart Component
 * Renders the primary box plot visualization with wind overlay and multi-year rider markers
 */

import { getDashboardData, getRouteData, getSelectedRider } from '../core/data.js';
import { calculateWindImpact } from '../core/gpxParser.js';
import { showTooltip, hideTooltip } from '../utils/domUtils.js';
import { formatTime } from '../utils/formatters.js';

/**
 * Render main box plot chart
 * @param {number} startYear - Start of year range filter
 * @param {number} endYear - End of year range filter
 */
export function render(startYear, endYear) {
  const dashboardData = getDashboardData();
  const routeData = getRouteData();
  const selectedRider = getSelectedRider();

  if (!dashboardData) return;

  const svg = document.getElementById('main-chart');
  svg.innerHTML = '';

  // Detect mobile
  const isMobile = window.innerWidth < 768;

  // Chart dimensions and scales (responsive)
  const width = 960;
  const height = 550;
  const marginLeft = isMobile ? 45 : 60;
  const marginRight = isMobile ? 20 : 40;
  const marginTop = 30;
  const marginBottom = isMobile ? 90 : 150;
  const chartWidth = width - marginLeft - marginRight;
  const chartHeight = height - marginTop - marginBottom;

  // Get filtered data
  const filteredData = dashboardData.statistics.by_year.filter(d => d.year >= startYear && d.year <= endYear);
  const filteredWeather = dashboardData.weather.by_year.filter(d => d.year >= startYear && d.year <= endYear);

  // Fixed Y-axis range: 40 to 100 minutes
  const minTime = 40;
  const maxTime = 100;

  // Y scale (INVERTED: faster times at TOP, slower times at BOTTOM)
  const yScale = (minutes) => {
    const normalized = (minutes - minTime) / (maxTime - minTime);
    return marginTop + normalized * chartHeight;
  };

  // X scale
  const xSpacing = chartWidth / (filteredData.length + 1);
  const xScale = (index) => marginLeft + (index + 1) * xSpacing;

  // Add grid pattern
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  const pattern = document.createElementNS('http://www.w3.org/2000/svg', 'pattern');
  pattern.setAttribute('id', 'grid');
  pattern.setAttribute('width', '80');
  pattern.setAttribute('height', '60');
  pattern.setAttribute('patternUnits', 'userSpaceOnUse');
  const gridPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  gridPath.setAttribute('d', 'M 80 0 L 0 0 0 60');
  gridPath.setAttribute('fill', 'none');
  gridPath.setAttribute('stroke', '#1f293b');
  gridPath.setAttribute('stroke-width', '1');
  pattern.appendChild(gridPath);
  defs.appendChild(pattern);
  svg.appendChild(defs);

  // Add grid background
  const gridRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  gridRect.setAttribute('x', '0');
  gridRect.setAttribute('y', '0');
  gridRect.setAttribute('width', width);
  gridRect.setAttribute('height', height);
  gridRect.setAttribute('fill', 'url(#grid)');
  svg.appendChild(gridRect);

  // Y-axis labels
  const yAxisGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  yAxisGroup.setAttribute('class', isMobile ? 'text-[9px] fill-slate-400' : 'text-[11px] fill-slate-400');
  const yValues = [40, 50, 60, 70, 80, 90, 100];
  yValues.forEach(minutes => {
    const y = yScale(minutes);
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', isMobile ? '2' : '6');
    text.setAttribute('y', y + 4);
    text.textContent = `${minutes}:00`;
    yAxisGroup.appendChild(text);
  });
  svg.appendChild(yAxisGroup);

  // X-axis labels (years)
  const xAxisGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  xAxisGroup.setAttribute('class', 'text-[12px] fill-slate-400');
  filteredData.forEach((d, i) => {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', xScale(i));
    text.setAttribute('y', marginTop + chartHeight + 15);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-weight', '600');
    text.textContent = d.year;
    xAxisGroup.appendChild(text);
  });
  svg.appendChild(xAxisGroup);

  // Horizontal leader lines at 10-minute intervals
  const leaderLinesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  leaderLinesGroup.setAttribute('id', 'layer-leader-lines');
  yValues.forEach(minutes => {
    const y = yScale(minutes);
    const leaderLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    leaderLine.setAttribute('x1', marginLeft);
    leaderLine.setAttribute('y1', y);
    leaderLine.setAttribute('x2', width - marginRight);
    leaderLine.setAttribute('y2', y);
    leaderLine.setAttribute('stroke', '#64748b');
    leaderLine.setAttribute('stroke-width', '1');
    leaderLine.setAttribute('opacity', '0.15');
    leaderLinesGroup.appendChild(leaderLine);
  });
  svg.appendChild(leaderLinesGroup);

  // Wind data section
  const windDataGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  windDataGroup.setAttribute('class', isMobile ? 'text-[8px] fill-slate-400' : 'text-[10px] fill-slate-400');

  // Headers for wind data (simplified on mobile)
  const windHeaders = isMobile ? [
    { label: 'Avg Wind:', y: marginTop + chartHeight + 25, color: '#0ea5e9' },
    { label: 'Riders:', y: marginTop + chartHeight + 55, color: '#10b981' }
  ] : [
    { label: 'Wind @ Base:', y: marginTop + chartHeight + 35, color: '#94a3b8' },
    { label: 'Wind @ Summit:', y: marginTop + chartHeight + 50, color: '#94a3b8' },
    { label: 'Average Wind:', y: marginTop + chartHeight + 65, color: '#0ea5e9' },
    { label: 'Total Riders:', y: marginTop + chartHeight + 110, color: '#10b981' }
  ];

  windHeaders.forEach(header => {
    const headerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    headerText.setAttribute('x', marginLeft - 5);
    headerText.setAttribute('y', header.y);
    headerText.setAttribute('text-anchor', 'end');
    headerText.setAttribute('font-weight', header.color === '#0ea5e9' ? '600' : '500');
    headerText.setAttribute('fill', header.color);
    headerText.textContent = header.label;
    windDataGroup.appendChild(headerText);
  });

  // Wind data values for each year
  filteredWeather.forEach((w, i) => {
    const x = xScale(i);
    const baseDir = w.start && w.start.wind_direction_avg !== null ? w.start.wind_direction_avg : null;
    const summitDir = w.summit && w.summit.wind_direction_avg !== null ? w.summit.wind_direction_avg : null;

    if (!isMobile) {
      // Desktop: Show detailed wind data
      // Wind at base (start)
      const baseWind = w.start && w.start.wind_speed_avg ? w.start.wind_speed_avg.toFixed(1) : 'N/A';

      const baseText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      baseText.setAttribute('x', x - 8);
      baseText.setAttribute('y', marginTop + chartHeight + 35);
      baseText.setAttribute('text-anchor', 'middle');
      baseText.setAttribute('fill', '#94a3b8');
      baseText.textContent = `${baseWind} mph`;
      windDataGroup.appendChild(baseText);

      // Small arrow for base wind direction
      if (baseDir !== null) {
        const smallArrowSize = 5;
        const baseArrowGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        baseArrowGroup.setAttribute('transform', `translate(${x + 18}, ${marginTop + chartHeight + 32}) rotate(${(baseDir + 180) % 360})`);

        const baseShaft = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        baseShaft.setAttribute('x1', '0');
        baseShaft.setAttribute('y1', smallArrowSize);
        baseShaft.setAttribute('x2', '0');
        baseShaft.setAttribute('y2', '-1');
        baseShaft.setAttribute('stroke', '#94a3b8');
        baseShaft.setAttribute('stroke-width', '1.5');
        baseArrowGroup.appendChild(baseShaft);

        const baseArrowHead = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        baseArrowHead.setAttribute('points', `0,-${smallArrowSize} -${smallArrowSize/2},0 ${smallArrowSize/2},0`);
        baseArrowHead.setAttribute('fill', '#94a3b8');
        baseArrowGroup.appendChild(baseArrowHead);

        windDataGroup.appendChild(baseArrowGroup);
      }

      // Wind at summit
      const summitWind = w.summit && w.summit.wind_speed_avg ? w.summit.wind_speed_avg.toFixed(1) : 'N/A';

      const summitText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      summitText.setAttribute('x', x - 8);
      summitText.setAttribute('y', marginTop + chartHeight + 50);
      summitText.setAttribute('text-anchor', 'middle');
      summitText.setAttribute('fill', '#94a3b8');
      summitText.textContent = `${summitWind} mph`;
      windDataGroup.appendChild(summitText);

      // Small arrow for summit wind direction
      if (summitDir !== null) {
        const smallArrowSize = 5;
        const summitArrowGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        summitArrowGroup.setAttribute('transform', `translate(${x + 18}, ${marginTop + chartHeight + 47}) rotate(${(summitDir + 180) % 360})`);

        const summitShaft = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        summitShaft.setAttribute('x1', '0');
        summitShaft.setAttribute('y1', smallArrowSize);
        summitShaft.setAttribute('x2', '0');
        summitShaft.setAttribute('y2', '-1');
        summitShaft.setAttribute('stroke', '#94a3b8');
        summitShaft.setAttribute('stroke-width', '1.5');
        summitArrowGroup.appendChild(summitShaft);

        const summitArrowHead = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        summitArrowHead.setAttribute('points', `0,-${smallArrowSize} -${smallArrowSize/2},0 ${smallArrowSize/2},0`);
        summitArrowHead.setAttribute('fill', '#94a3b8');
        summitArrowGroup.appendChild(summitArrowHead);

        windDataGroup.appendChild(summitArrowGroup);
      }
    }

    // Average wind (shown on both mobile and desktop)
    const avgWind = (w.start && w.summit && w.start.wind_speed_avg && w.summit.wind_speed_avg)
      ? ((w.start.wind_speed_avg + w.summit.wind_speed_avg) / 2).toFixed(1)
      : 'N/A';
    const avgText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    avgText.setAttribute('x', x);
    avgText.setAttribute('y', isMobile ? marginTop + chartHeight + 25 : marginTop + chartHeight + 65);
    avgText.setAttribute('text-anchor', 'middle');
    avgText.setAttribute('fill', '#0ea5e9');
    avgText.setAttribute('font-weight', '600');
    avgText.textContent = `${avgWind}`;
    windDataGroup.appendChild(avgText);

    // Wind direction arrow (average of base and summit directions)
    if (baseDir !== null && summitDir !== null) {
      const avgDir = ((baseDir + summitDir) / 2) % 360;
      const arrowY = isMobile ? marginTop + chartHeight + 38 : marginTop + chartHeight + 80;
      const arrowSize = isMobile ? 5 : 8;

      const arrowGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      arrowGroup.setAttribute('transform', `translate(${x}, ${arrowY}) rotate(${(avgDir + 180) % 360})`);

      const shaft = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      shaft.setAttribute('x1', '0');
      shaft.setAttribute('y1', arrowSize);
      shaft.setAttribute('x2', '0');
      shaft.setAttribute('y2', isMobile ? '0' : '-2');
      shaft.setAttribute('stroke', '#0ea5e9');
      shaft.setAttribute('stroke-width', isMobile ? '1.5' : '2');
      arrowGroup.appendChild(shaft);

      const arrowHead = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
      arrowHead.setAttribute('points', `0,-${arrowSize} -${arrowSize/2},0 ${arrowSize/2},0`);
      arrowHead.setAttribute('fill', '#0ea5e9');
      arrowGroup.appendChild(arrowHead);

      windDataGroup.appendChild(arrowGroup);
    }

    // Total riders count
    const riderCount = filteredData[i] ? filteredData[i].count : 'N/A';
    const ridersText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    ridersText.setAttribute('x', x);
    ridersText.setAttribute('y', isMobile ? marginTop + chartHeight + 55 : marginTop + chartHeight + 110);
    ridersText.setAttribute('text-anchor', 'middle');
    ridersText.setAttribute('fill', '#10b981');
    ridersText.setAttribute('font-weight', '600');
    ridersText.textContent = riderCount;
    windDataGroup.appendChild(ridersText);
  });

  svg.appendChild(windDataGroup);

  // Weather layer (wind overlay)
  const weatherLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  weatherLayer.setAttribute('id', 'layer-wind');
  weatherLayer.setAttribute('opacity', '1');

  filteredWeather.forEach((w, i) => {
    if (w.summit && w.summit.wind_speed_avg) {
      const windSpeed = w.summit.wind_speed_avg;
      const windDirection = w.summit.wind_direction_avg;

      let fillColor, opacity;

      if (routeData && windDirection !== null) {
        const impact = calculateWindImpact(windDirection, routeData);
        const baseOpacity = Math.min(0.4, windSpeed / 30);

        if (impact.impact === 'beneficial') {
          fillColor = `rgba(34, 197, 94, ${baseOpacity})`;
        } else if (impact.impact === 'detrimental') {
          fillColor = `rgba(239, 68, 68, ${baseOpacity})`;
        } else {
          fillColor = `rgba(251, 191, 36, ${baseOpacity})`;
        }
        opacity = 1;
      } else {
        const baseOpacity = Math.min(0.3, windSpeed / 40);
        fillColor = `rgba(14, 165, 233, ${baseOpacity})`;
        opacity = 1;
      }

      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', xScale(i) - xSpacing/3);
      rect.setAttribute('y', marginTop);
      rect.setAttribute('width', xSpacing * 0.66);
      rect.setAttribute('height', chartHeight);
      rect.setAttribute('fill', fillColor);
      rect.setAttribute('opacity', opacity);
      weatherLayer.appendChild(rect);
    }
  });
  svg.appendChild(weatherLayer);

  // Box plot layer
  const boxPlotLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  boxPlotLayer.setAttribute('id', 'layer-boxplot');

  filteredData.forEach((d, i) => {
    const x = xScale(i);
    const boxWidth = Math.min(20, xSpacing * 0.4);

    // Draw box (25th to 75th percentile)
    const box = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    box.setAttribute('x', x - boxWidth/2);
    box.setAttribute('y', yScale(d.times.p25));
    box.setAttribute('width', boxWidth);
    box.setAttribute('height', yScale(d.times.p75) - yScale(d.times.p25));
    box.setAttribute('fill', '#94a3b814');
    box.setAttribute('stroke', '#64748b');
    box.setAttribute('stroke-width', '1');
    box.setAttribute('cursor', 'pointer');
    box.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} IQR</strong><br/>
      25th percentile: ${d.times_formatted.p25}<br/>
      75th percentile: ${d.times_formatted.p75}
    `));
    box.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(box);

    // 25th percentile marker
    const p25Marker = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    p25Marker.setAttribute('x1', x - boxWidth/2);
    p25Marker.setAttribute('y1', yScale(d.times.p25));
    p25Marker.setAttribute('x2', x + boxWidth/2);
    p25Marker.setAttribute('y2', yScale(d.times.p25));
    p25Marker.setAttribute('stroke', '#64748b');
    p25Marker.setAttribute('stroke-width', '1.5');
    p25Marker.setAttribute('cursor', 'pointer');
    p25Marker.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} 25th Percentile</strong><br/>
      ${d.times_formatted.p25}
    `));
    p25Marker.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(p25Marker);

    // 75th percentile marker
    const p75Marker = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    p75Marker.setAttribute('x1', x - boxWidth/2);
    p75Marker.setAttribute('y1', yScale(d.times.p75));
    p75Marker.setAttribute('x2', x + boxWidth/2);
    p75Marker.setAttribute('y2', yScale(d.times.p75));
    p75Marker.setAttribute('stroke', '#64748b');
    p75Marker.setAttribute('stroke-width', '1.5');
    p75Marker.setAttribute('cursor', 'pointer');
    p75Marker.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} 75th Percentile</strong><br/>
      ${d.times_formatted.p75}
    `));
    p75Marker.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(p75Marker);

    // Median line with triangle markers
    const medianLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    medianLine.setAttribute('x1', x - boxWidth/2);
    medianLine.setAttribute('y1', yScale(d.times.median));
    medianLine.setAttribute('x2', x + boxWidth/2);
    medianLine.setAttribute('y2', yScale(d.times.median));
    medianLine.setAttribute('stroke', '#0f766e');
    medianLine.setAttribute('stroke-width', '2');
    medianLine.setAttribute('cursor', 'pointer');
    medianLine.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} Median</strong><br/>
      ${d.times_formatted.median}
    `));
    medianLine.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(medianLine);

    // Median triangle markers
    const triangleSize = 3;
    const medianY = yScale(d.times.median);

    const medianTriangleLeft = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    const leftX = x - boxWidth/2;
    medianTriangleLeft.setAttribute('points', `${leftX},${medianY} ${leftX-triangleSize},${medianY-triangleSize} ${leftX-triangleSize},${medianY+triangleSize}`);
    medianTriangleLeft.setAttribute('fill', '#0f766e');
    medianTriangleLeft.setAttribute('cursor', 'pointer');
    medianTriangleLeft.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} Median</strong><br/>
      ${d.times_formatted.median}
    `));
    medianTriangleLeft.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(medianTriangleLeft);

    const medianTriangleRight = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    const rightX = x + boxWidth/2;
    medianTriangleRight.setAttribute('points', `${rightX},${medianY} ${rightX+triangleSize},${medianY-triangleSize} ${rightX+triangleSize},${medianY+triangleSize}`);
    medianTriangleRight.setAttribute('fill', '#0f766e');
    medianTriangleRight.setAttribute('cursor', 'pointer');
    medianTriangleRight.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} Median</strong><br/>
      ${d.times_formatted.median}
    `));
    medianTriangleRight.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(medianTriangleRight);

    // Mean dot
    const meanDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    meanDot.setAttribute('cx', x);
    meanDot.setAttribute('cy', yScale(d.times.mean));
    meanDot.setAttribute('r', '4.5');
    meanDot.setAttribute('fill', '#6366f1');
    meanDot.setAttribute('cursor', 'pointer');
    meanDot.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} Mean</strong><br/>
      ${d.times_formatted.mean}
    `));
    meanDot.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(meanDot);

    // 10th percentile
    const p10Time = d.times.p25 - (d.times.p25 - d.times.min) * 0.6;
    const p10Formatted = formatTime(p10Time);

    // Line from 10th percentile to fastest time
    const p10ToMinLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    p10ToMinLine.setAttribute('x1', x);
    p10ToMinLine.setAttribute('y1', yScale(p10Time));
    p10ToMinLine.setAttribute('x2', x);
    p10ToMinLine.setAttribute('y2', yScale(d.times.min));
    p10ToMinLine.setAttribute('stroke', '#ef4444');
    p10ToMinLine.setAttribute('stroke-width', '1.5');
    p10ToMinLine.setAttribute('stroke-dasharray', '3,3');
    p10ToMinLine.setAttribute('opacity', '0.8');
    boxPlotLayer.appendChild(p10ToMinLine);

    // Line from 25th to 10th percentile
    const p25ToP10Line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    p25ToP10Line.setAttribute('x1', x);
    p25ToP10Line.setAttribute('y1', yScale(d.times.p25));
    p25ToP10Line.setAttribute('x2', x);
    p25ToP10Line.setAttribute('y2', yScale(p10Time));
    p25ToP10Line.setAttribute('stroke', '#eab308');
    p25ToP10Line.setAttribute('stroke-width', '1.5');
    p25ToP10Line.setAttribute('stroke-dasharray', '3,3');
    p25ToP10Line.setAttribute('opacity', '0.8');
    boxPlotLayer.appendChild(p25ToP10Line);

    // 10th percentile dot
    const p10Dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    p10Dot.setAttribute('cx', x);
    p10Dot.setAttribute('cy', yScale(p10Time));
    p10Dot.setAttribute('r', '4.5');
    p10Dot.setAttribute('fill', '#eab308');
    p10Dot.setAttribute('cursor', 'pointer');
    p10Dot.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} 10th Percentile</strong><br/>
      Top 10% of finishers<br/>
      ${p10Formatted}
    `));
    p10Dot.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(p10Dot);

    // Fastest time dot
    const fastestDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    fastestDot.setAttribute('cx', x);
    fastestDot.setAttribute('cy', yScale(d.times.min));
    fastestDot.setAttribute('r', '4.5');
    fastestDot.setAttribute('fill', '#ef4444');
    fastestDot.setAttribute('cursor', 'pointer');
    fastestDot.addEventListener('mouseenter', (e) => showTooltip(e, `
      <strong class="text-slate-100">${d.year} Fastest Time</strong><br/>
      ${d.times_formatted.min}
    `));
    fastestDot.addEventListener('mouseleave', hideTooltip);
    boxPlotLayer.appendChild(fastestDot);
  });

  svg.appendChild(boxPlotLayer);

  // Multi-year rider stars layer
  const multiYearRidersLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  multiYearRidersLayer.setAttribute('id', 'layer-multi-year-riders');

  if (selectedRider) {
    filteredData.forEach((d, i) => {
      const x = xScale(i);
      const year = d.year;

      const performance = selectedRider.performances.find(p => p.year === year);

      if (performance) {
        const timeMinutes = performance.time_seconds / 60;
        const y = yScale(timeMinutes);

        const star = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        star.setAttribute('x', x);
        star.setAttribute('y', y + 1);
        star.setAttribute('text-anchor', 'middle');
        star.setAttribute('font-size', '14');
        star.setAttribute('fill', '#fbbf24');
        star.setAttribute('cursor', 'pointer');
        star.setAttribute('class', 'star-marker');
        star.textContent = '★';

        star.addEventListener('mouseenter', (e) => showTooltip(e, `
          <strong class="text-amber-400">★ ${selectedRider.name}</strong><br/>
          ${year}: ${performance.time_formatted} (Place ${performance.place})
        `));
        star.addEventListener('mouseleave', hideTooltip);

        multiYearRidersLayer.appendChild(star);
      }
    });
  }

  svg.appendChild(multiYearRidersLayer);

  // Median trend line
  const medianLineLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  medianLineLayer.setAttribute('id', 'layer-median-line');

  let pathData = '';
  filteredData.forEach((d, i) => {
    const x = xScale(i);
    const y = yScale(d.times.median);
    if (i === 0) {
      pathData += `M ${x} ${y}`;
    } else {
      pathData += ` L ${x} ${y}`;
    }
  });

  const medianPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  medianPath.setAttribute('d', pathData);
  medianPath.setAttribute('fill', 'none');
  medianPath.setAttribute('stroke', '#0f766e');
  medianPath.setAttribute('stroke-width', '2.5');
  medianPath.setAttribute('stroke-linejoin', 'round');
  medianLineLayer.appendChild(medianPath);

  svg.appendChild(medianLineLayer);
}
