import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Paper, CircularProgress, Chip, Button } from '@mui/material';
import ForceGraph2D from 'react-force-graph-2d';
import { useNavigate } from 'react-router-dom';
import { GraphNode, GraphLink, GraphData } from '../../types';

interface KnowledgeGraphProps {
  rootIds?: string[];
  maxDepth?: number;
  width?: number;
  height?: number;
  onNodeClick?: (nodeId: string) => void;
}

const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({
  rootIds,
  maxDepth = 2,
  width,
  height = 600,
  onNodeClick
}) => {
  const navigate = useNavigate();
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightNodes, setHighlightNodes] = useState(new Set<string>());
  const [highlightLinks, setHighlightLinks] = useState(new Set<string>());
  const [hoverNode, setHoverNode] = useState<GraphNode | null>(null);
  
  const fgRef = useRef<any>();
  
  // Load graph data on component mount
  useEffect(() => {
    fetchGraphData();
  }, [rootIds, maxDepth]);
  
  const fetchGraphData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch graph data from API
      const response = await fetch(`/api/graph/knowledge?${rootIds ? `rootIds=${rootIds.join(',')}` : ''}&maxDepth=${maxDepth}`);
      const data = await response.json();
      
      if (data && data.nodes && data.links) {
        // Process nodes to add visualization properties
        const processedNodes = data.nodes.map((node: GraphNode) => ({
          ...node,
          val: getNodeSize(node.type),
          color: getNodeColor(node.type, node.category)
        }));
        
        // Process links to add visualization properties
        const processedLinks = data.links.map((link: GraphLink) => ({
          ...link,
          value: getLinkStrength(link.type),
          color: getLinkColor(link.type)
        }));
        
        setGraphData({
          nodes: processedNodes,
          links: processedLinks
        });
      } else {
        throw new Error("Invalid graph data format");
      }
    } catch (err) {
      console.error("Error fetching graph data:", err);
      setError("Failed to load knowledge graph. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  const getNodeSize = (type: string): number => {
    switch (type) {
      case 'folder':
        return 5;
      case 'note':
        return 3;
      case 'todo':
        return 2.5;
      case 'calendar':
        return 2.5;
      default:
        return 2;
    }
  };
  
  const getNodeColor = (type: string, category?: string): string => {
    // First determine color by type
    let color;
    switch (type) {
      case 'folder':
        color = '#2196f3'; // blue
        break;
      case 'note':
        color = '#4caf50'; // green
        break;
      case 'todo':
        color = '#f44336'; // red
        break;
      case 'calendar':
        color = '#ff9800'; // orange
        break;
      default:
        color = '#9e9e9e'; // gray
    }
    
    // If it's a note, use category to adjust color shade
    if (type === 'note' && category) {
      switch (category.toLowerCase()) {
        case 'personal':
          color = '#66bb6a';  // lighter green
          break;
        case 'work':
          color = '#388e3c';  // darker green
          break;
        case 'research':
          color = '#81c784';  // medium green
          break;
      }
    }
    
    return color;
  };
  
  const getLinkStrength = (type?: string): number => {
    if (!type) return 1;
    
    switch (type.toLowerCase()) {
      case 'contains':
      case 'parent':
        return 2;
      case 'references':
      case 'related':
        return 1;
      case 'weak_connection':
        return 0.5;
      default:
        return 1;
    }
  };
  
  const getLinkColor = (type?: string): string => {
    if (!type) return '#cccccc';
    
    switch (type.toLowerCase()) {
      case 'contains':
      case 'parent':
        return '#555555';
      case 'references':
        return '#9c27b0';
      case 'related':
        return '#3f51b5';
      case 'weak_connection':
        return '#e0e0e0';
      default:
        return '#cccccc';
    }
  };
  
  const handleNodeClick = (node: GraphNode) => {
    if (onNodeClick) {
      onNodeClick(node.id);
    } else {
      // Default action - navigate to content view
      navigate(`/content/${node.id}`);
    }
  };
  
  const handleNodeHover = (node: GraphNode | null) => {
    setHoverNode(node);
    
    // Reset highlights
    setHighlightNodes(new Set());
    setHighlightLinks(new Set());
    
    if (node) {
      // Set node highlight
      setHighlightNodes(new Set([node.id]));
      
      // Find and highlight connected links and nodes
      if (graphData.links) {
        const connectedLinks = graphData.links.filter(
          link => {
            const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
            const targetId = typeof link.target === 'object' ? link.target.id : link.target;
            return sourceId === node.id || targetId === node.id;
          }
        );
        
        setHighlightLinks(new Set(connectedLinks.map(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
          return sourceId + '-' + targetId;
        })));
        
        // Highlight connected nodes
        const connectedNodeIds = new Set<string>();
        connectedLinks.forEach(link => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
          const targetId = typeof link.target === 'object' ? link.target.id : link.target;
          connectedNodeIds.add(sourceId);
          connectedNodeIds.add(targetId);
        });
        
        setHighlightNodes(connectedNodeIds);
      }
    }
  };
  
  return (
    <Paper sx={{ p: 2, height: height + 50, position: 'relative' }}>
      <Typography variant="h6" gutterBottom>
        Knowledge Graph
        {rootIds && rootIds.length > 0 && (
          <Chip 
            label={`${rootIds.length} Root Item${rootIds.length > 1 ? 's' : ''}`} 
            size="small" 
            sx={{ ml: 1 }} 
          />
        )}
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: height }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: height }}>
          <Typography color="error">{error}</Typography>
        </Box>
      ) : graphData.nodes.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: height }}>
          <Typography color="textSecondary">No graph data available</Typography>
        </Box>
      ) : (
        <Box sx={{ height: height }}>
          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            nodeLabel={(node: GraphNode) => `${node.name} (${node.type})`}
            linkLabel={(link: GraphLink) => link.type || 'related'}
            nodeRelSize={6}
            nodeVal={(node: GraphNode) => node.val || 1}
            nodeColor={(node: GraphNode) => 
              highlightNodes.has(node.id) ? '#ff5722' : node.color || '#9e9e9e'
            }
            linkWidth={(link: GraphLink) => {
              const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
              const targetId = typeof link.target === 'object' ? link.target.id : link.target;
              return highlightLinks.has(sourceId + '-' + targetId) ? 3 : 1;
            }}
            linkColor={(link: GraphLink) => {
              const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
              const targetId = typeof link.target === 'object' ? link.target.id : link.target;
              return highlightLinks.has(sourceId + '-' + targetId) ? '#ff5722' : link.color || '#cccccc';
            }}
            onNodeClick={handleNodeClick}
            onNodeHover={handleNodeHover}
            width={width}
            height={height}
          />
          
          {hoverNode && (
            <Box 
              sx={{ 
                position: 'absolute', 
                top: 10, 
                right: 10, 
                p: 2, 
                bgcolor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                boxShadow: 1
              }}
            >
              <Typography variant="subtitle2">{hoverNode.name}</Typography>
              <Typography variant="caption" display="block">
                Type: {hoverNode.type}
              </Typography>
              {hoverNode.category && (
                <Typography variant="caption" display="block">
                  Category: {hoverNode.category}
                </Typography>
              )}
              <Button 
                size="small" 
                sx={{ mt: 1 }} 
                onClick={() => handleNodeClick(hoverNode)}
              >
                View Details
              </Button>
            </Box>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default KnowledgeGraph; 