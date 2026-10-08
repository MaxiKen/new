// Convert world-atlas countries-10m TopoJSON -> GeoJSON for Nigeria (and neighbours) using topojson-client if available,
// otherwise a minimal decoder.
const fs = require('fs');
const path = require('path');
const topo = JSON.parse(fs.readFileSync(path.join(__dirname, 'package', 'countries-10m.json'), 'utf8'));
function decodeArcs(topo) {
  const tr = topo.transform;
  return topo.arcs.map(arc => {
    let x = 0, y = 0;
    return arc.map(([dx, dy]) => {
      x += dx; y += dy;
      return tr ? [x * tr.scale[0] + tr.translate[0], y * tr.scale[1] + tr.translate[1]] : [x, y];
    });
  });
}
const arcs = decodeArcs(topo);
function arcRing(indices) {
  let coords = [];
  for (const i of indices) {
    const a = i >= 0 ? arcs[i] : arcs[~i].slice().reverse();
    coords = coords.concat(coords.length ? a.slice(1) : a);
  }
  return coords;
}
function polyCoords(arcIdx) { return arcIdx.map(arcRing); }
const feats = [];
for (const g of topo.objects.countries.geometries) {
  if (!['Nigeria', 'Benin', 'Niger', 'Chad', 'Cameroon', 'Togo', 'Ghana'].includes(g.properties.name)) continue;
  let geom;
  if (g.type === 'Polygon') geom = { type: 'Polygon', coordinates: polyCoords(g.arcs) };
  else if (g.type === 'MultiPolygon') geom = { type: 'MultiPolygon', coordinates: g.arcs.map(polyCoords) };
  feats.push({ type: 'Feature', properties: { name: g.properties.name, id: g.id }, geometry: geom });
}
fs.writeFileSync(path.join(__dirname, 'countries_sel.geojson'), JSON.stringify({ type: 'FeatureCollection', features: feats }));
console.log('features', feats.map(f => f.properties.name));
