import React, { useEffect, useRef, useState, useMemo } from 'react';
import { Box, CircularProgress, Typography, Paper } from '@mui/material';
import ForceGraph2D from 'react-force-graph-2d';
import { GraphData, GraphNode, GraphLink } from '../../types';
import api from '../../services/api';

interface KnowledgeGraphProps {
  rootIds?: string[];
  maxDepth?: number;
  height?: number;
  width?: number;
  onNodeClick?: (node: GraphNode) => void;
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({
  rootIds,
  maxDepth = 2,
  height = 600,
  width,
  onNodeClick
}) => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightNodes, setHighlightNodes] = useState(new Set<string>());
  const [highlightLinks, setHighlightLinks] = useState(new Set<string>());
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  const graphRef = useRef<any>(null);

  // Type colors for nodes
  const nodeColors = useMemo(() => ({
    note: '#2196f3',
    todo: '#673ab7',
    calendar: '#ff9800',
    folder: '#4caf50',
    category: '#9e9e9e',
    tag: '#e91e63'
  }), []);

  // Fetch graph data
  useEffect(() => {
    const fetchGraphData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await api.getKnowledgeGraph(rootIds, maxDepth);
        
        if (data && data.nodes && data.links) {
          // Process node colors based on type
          const processedData = {
            nodes: data.nodes.map((node: GraphNode) => ({
              ...node,
              color: node.color || nodeColors[node.type as keyof typeof nodeColors] || '#999',
              val: node.val || 1
            })),
            links: data.links
          };
          
          setGraphData(processedData);
        } else {
          setError('Invalid data structure received from API');
        }
      } catch (error) {
        console.error('Error fetching graph data:', error);
        setError('Failed to load knowledge graph data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraphData();
  }, [rootIds, maxDepth, nodeColors]);

  // Handle node hover - highlight connected nodes and links
  const handleNodeHover = (node: GraphNode | null) => {
    highlightNodes.clear();
    highlightLinks.clear();

    if (node) {
      highlightNodes.add(node.id);
      
      if (graphData) {
        graphData.links.forEach(link => {
          const source = typeof link.source === 'object' ? link.source.id : link.source;
          const target = typeof link.target === 'object' ? link.target.id : link.target;
          
          if (source === node.id || target === node.id) {
            highlightLinks.add(`${source}-${target}`);
            highlightNodes.add(source);
            highlightNodes.add(target);
          }
        });
      }
    }

    setHighlightLinks(new Set(highlightLinks));
    setHighlightNodes(new Set(highlightNodes));
  };

  // Handle node click
  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
    if (onNodeClick) {
      onNodeClick(node);
    }
  };

  // Calculate node size based on connections
  const getNodeSize = (node: GraphNode) => {
    if (!graphData) return 8;
    
    let connectionCount = 0;
    graphData.links.forEach(link => {
      const source = typeof link.source === 'object' ? link.source.id : link.source;
      const target = typeof link.target === 'object' ? link.target.id : link.target;
      
      if (source === node.id || target === node.id) {
        connectionCount++;
      }
    });
    
    // Base size + bonus for connections
    return 8 + Math.min(connectionCount * 2, 12);
  };

  // Custom link color based on relationship type
  const getLinkColor = (link: GraphLink) => {
    if (highlightLinks.has(`${link.source}-${link.target}`)) {
      return '#ff5722';
    }
    
    switch (link.type) {
      case 'related':
        return '#2196f3';
      case 'parent':
        return '#4caf50';
      case 'reference':
        return '#ff9800';
      default:
        return '#999';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height }}>
        <Typography>No data available for knowledge graph</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ position: 'relative' }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        height={height}
        width={width}
        nodeRelSize={8}
        nodeVal={node => (highlightNodes.has(node.id) ? 1.5 : 1) * (node.val || 1)}
        nodeLabel={node => `${node.name} (${node.type})`}
        nodeColor={node => highlightNodes.has(node.id) ? '#ff5722' : (node.color || '#999')}
        nodeCanvasObjectMode={() => 'after'}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 14 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
          
          // Draw node label - only if zoomed in enough
          if (globalScale >= 0.8) {
            ctx.fillText(label, node.x || 0, (node.y || 0) + 10);
          }
          
          // Draw different shapes for different content types
          ctx.beginPath();
          const size = getNodeSize(node);
          
          switch(node.type) {
            case 'note':
              // Draw rectangle
              ctx.rect((node.x || 0) - size/2, (node.y || 0) - size/2, size, size);
              break;
            case 'todo':
              // Draw diamond
              ctx.moveTo(node.x || 0, (node.y || 0) - size/2);
              ctx.lineTo((node.x || 0) + size/2, node.y || 0);
              ctx.lineTo(node.x || 0, (node.y || 0) + size/2);
              ctx.lineTo((node.x || 0) - size/2, node.y || 0);
              break;
            case 'calendar':
              // Draw triangle
              ctx.moveTo(node.x || 0, (node.y || 0) - size/2);
              ctx.lineTo((node.x || 0) + size/2, (node.y || 0) + size/2);
              ctx.lineTo((node.x || 0) - size/2, (node.y || 0) + size/2);
              break;
            default:
              // Draw circle
              ctx.arc(node.x || 0, node.y || 0, size/2, 0, 2 * Math.PI);
          }
          
          ctx.fillStyle = highlightNodes.has(node.id) ? '#ff5722' : (node.color || '#999');
          ctx.fill();
        }}
        linkColor={link => getLinkColor(link)}
        linkWidth={link => highlightLinks.has(`${link.source}-${link.target}`) ? 3 : 1}
        linkDirectionalArrowLength={link => link.type === 'parent' ? 3 : 0}
        linkDirectionalArrowRelPos={0.8}
        linkDirectionalParticles={link => highlightLinks.has(`${link.source}-${link.target}`) ? 4 : 0}
        linkDirectionalParticleWidth={2}
        onNodeHover={handleNodeHover}
        onNodeClick={handleNodeClick}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.1}
      />

      {selectedNode && (
        <Paper
          sx={{
            position: 'absolute',
            bottom: 20,
            right: 20,
            p: 2,
            maxWidth: 300,
            zIndex: 1000
          }}
        >
          <Typography variant="h6" gutterBottom>
            {selectedNode.name}
          </Typography>
          <Typography variant="body2">
            <strong>Type:</strong> {selectedNode.type}
          </Typography>
          {selectedNode.category && (
            <Typography variant="body2">
              <strong>Category:</strong> {selectedNode.category}
            </Typography>
          )}
          <Typography variant="body2">
            <strong>Connections:</strong> {
              graphData.links.filter(link => {
                const source = typeof link.source === 'object' ? link.source.id : link.source;
                const target = typeof link.target === 'object' ? link.target.id : link.target;
                return source === selectedNode.id || target === selectedNode.id;
              }).length
            }
          </Typography>
        </Paper>
      )}

      {/* Legend */}
      <Box
        sx={{
          position: 'absolute',
          top: 20,
          left: 20,
          p: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          borderRadius: 1,
          zIndex: 1000
        }}
      >
        <Typography variant="subtitle2" gutterBottom>
          Node Types
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {Object.entries(nodeColors).map(([type, color]) => (
            <Box key={type} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  backgroundColor: color,
                  borderRadius: '50%'
                }}
              />
              <Typography variant="caption">
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default KnowledgeGraph; 