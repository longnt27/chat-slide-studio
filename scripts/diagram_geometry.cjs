'use strict';
/**
 * Content-driven diagram geometry shared by the renderer and regression tests.
 *
 * Relationships, not item counts, determine meaning:
 *   peers       = equal concepts with no direction implied
 *   hierarchy   = a parent and equally ranked children
 *   reciprocal  = two sides interacting in both directions
 *
 * An incomplete final row is centered; no orphan tile is left aligned.
 * These are default heuristics, not mandates for every diagram.
 */
const RELATIONSHIPS = Object.freeze(['peers','hierarchy','reciprocal']);

function chooseColumns(count) {
  if (!Number.isInteger(count) || count < 1 || count > 9)
    throw Error('Diagram supports between 1 and 9 peers');
  if (count <= 4) return count;
  if (count <= 6) return 3;
  if (count <= 8) return 4;
  return 3;
}
function balancedGrid(count, area, options={}) {
  const columns = options.columns || chooseColumns(count);
  if (!Number.isInteger(columns) || columns < 1 || columns > 4)
    throw Error('Columns must be between 1 and 4');
  const gapX = options.gapX ?? 0.20, gapY = options.gapY ?? 0.17;
  const rows = Math.ceil(count / columns);
  const tileW = (area.w - (columns - 1) * gapX) / columns;
  const tileH = Math.min(options.maxTileH ?? 0.74,
    (area.h - (rows - 1) * gapY) / rows);
  if (tileW < 0.8 || tileH < 0.35) throw Error('Diagram too dense; split into more slides');
  const usedH = rows * tileH + (rows - 1) * gapY;
  const y0 = area.y + (area.h - usedH) / 2;
  const tiles=[];
  for (let i=0;i<count;i++) {
    const row = Math.floor(i/columns), col=i%columns;
    const rowCount = Math.min(columns, count-row*columns);
    const rowW = rowCount*tileW+(rowCount-1)*gapX;
    const rowX = area.x + (area.w - rowW)/2;
    tiles.push({x:rowX+col*(tileW+gapX),y:y0+row*(tileH+gapY),
      w:tileW,h:tileH,row,col});
  }
  return {tiles,columns,rows,centerX:area.x+area.w/2};
}
function planDiagram(relationship,count,rect) {
  if (!RELATIONSHIPS.includes(relationship))
    throw Error('Unknown relationship: '+relationship);
  const {x,y,w} = rect;
  const bottom={x,y:6.12,w,h:0.54};
  const caption={x,y:6.77,w,h:0.22};
  if(relationship==='reciprocal') {
    const rootW=w*0.375,groupW=w*0.445;
    const root={x,y:3.59,w:rootW,h:1.30};
    const peersArea={x:x+w-groupW,y:2.73,w:groupW,h:3.07};
    const grid=balancedGrid(count,peersArea,
      {columns:count<=3?1:count<=6?2:3,maxTileH:0.82,gapX:0.13,gapY:0.19});
    const gapStart=x+rootW, gapEnd=peersArea.x;
    const arrow={x:gapStart+0.12,y:4.08,w:gapEnd-gapStart-0.24,h:0.38};
    const relLabel={x:gapStart-0.09,y:3.45,w:gapEnd-gapStart+0.18,h:0.44};
    const peerLabel={x:peersArea.x,y:2.18,w:groupW,h:0.30};
    return {relationship,root,grid,arrow,relLabel,peerLabel,bottom,caption,
      centerX:x+w/2};
  }
  const root=relationship==='hierarchy'?
    {x,y:2.17,w,h:0.68}:{x,y:2.22,w,h:0.40};
  const peerLabel={x:x+(w-3.74)/2,y:relationship==='hierarchy'?3.07:2.85,
    w:3.74,h:0.45};
  const grid=balancedGrid(count,
    {x,y:relationship==='hierarchy'?3.76:3.66,w,h:2.05},
    {maxTileH:0.75,gapX:0.20,gapY:0.18});
  return {relationship,root,peerLabel,grid,bottom,caption,centerX:x+w/2};
}
module.exports={RELATIONSHIPS,chooseColumns,balancedGrid,planDiagram};
