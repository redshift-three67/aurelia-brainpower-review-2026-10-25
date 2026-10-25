/**
 * Gruppenanalyse-Panel
 * Verwaltung von Klienten-Gruppen mit Vektor-Vergleich
 */
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Plus,
  Trash2,
  UserPlus,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Loader2,
  X,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useClientGroups, type ClientGroup, type GroupMember, type GroupVectorSummary } from '@/hooks/useClientGroups';
import { useClientDatabase, type ClientRecord } from '@/hooks/useClientDatabase';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const DIMENSION_COLORS = [
  'hsl(var(--primary))',
  'hsl(var(--accent))',
  'hsl(210, 80%, 55%)',
  'hsl(150, 70%, 45%)',
  'hsl(0, 70%, 55%)',
];

function RadarChart({ summary }: { summary: GroupVectorSummary }) {
  const size = 200;
  const center = size / 2;
  const radius = 75;
  const dims = summary.avgDimensions;
  const labels = summary.dimensionLabels;
  const angleStep = (2 * Math.PI) / 5;

  const getPoint = (value: number, index: number) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = (Math.min(Math.max(value, 0), 10) / 10) * radius;
    return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
  };

  // Grid lines
  const gridLevels = [2, 4, 6, 8, 10];

  return (
    <svg viewBox={`0 0 ${size} ${size}`} className="w-full max-w-[220px] mx-auto">
      {/* Grid */}
      {gridLevels.map(level => (
        <polygon
          key={level}
          points={Array.from({ length: 5 }, (_, i) => {
            const p = getPoint(level, i);
            return `${p.x},${p.y}`;
          }).join(' ')}
          fill="none"
          stroke="hsl(var(--border))"
          strokeWidth="0.5"
          opacity={0.4}
        />
      ))}

      {/* Axes */}
      {Array.from({ length: 5 }, (_, i) => {
        const p = getPoint(10, i);
        return <line key={i} x1={center} y1={center} x2={p.x} y2={p.y} stroke="hsl(var(--border))" strokeWidth="0.5" opacity={0.3} />;
      })}

      {/* Average polygon */}
      <polygon
        points={dims.map((d, i) => {
          const p = getPoint(d, i);
          return `${p.x},${p.y}`;
        }).join(' ')}
        fill="hsl(var(--primary) / 0.2)"
        stroke="hsl(var(--primary))"
        strokeWidth="1.5"
      />

      {/* Individual member polygons */}
      {summary.members.map((member, mi) => (
        <polygon
          key={mi}
          points={member.dimensions.map((d, i) => {
            const p = getPoint(d, i);
            return `${p.x},${p.y}`;
          }).join(' ')}
          fill="none"
          stroke={DIMENSION_COLORS[mi % DIMENSION_COLORS.length]}
          strokeWidth="0.8"
          opacity={0.5}
          strokeDasharray="3,2"
        />
      ))}

      {/* Dots */}
      {dims.map((d, i) => {
        const p = getPoint(d, i);
        return <circle key={i} cx={p.x} cy={p.y} r="3" fill={DIMENSION_COLORS[i]} />;
      })}

      {/* Labels */}
      {labels.map((label, i) => {
        const p = getPoint(12, i);
        return (
          <text
            key={i}
            x={p.x}
            y={p.y}
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-muted-foreground"
            fontSize="7"
          >
            {label}
          </text>
        );
      })}
    </svg>
  );
}

export default function GroupManagementPanel() {
  const {
    groups, isLoading, loadGroups, createGroup, deleteGroup,
    loadGroupMembers, addMember, removeMember, getGroupVectorSummary,
  } = useClientGroups();

  const { clients, loadClients } = useClientDatabase();

  const [newGroupName, setNewGroupName] = useState('');
  const [expandedGroupId, setExpandedGroupId] = useState<string | null>(null);
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [vectorSummary, setVectorSummary] = useState<GroupVectorSummary | null>(null);
  const [addClientId, setAddClientId] = useState<string>('');
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  useEffect(() => {
    loadGroups();
    loadClients();
  }, [loadGroups, loadClients]);

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) return;
    await createGroup(newGroupName.trim());
    setNewGroupName('');
  };

  const handleExpand = async (group: ClientGroup) => {
    if (expandedGroupId === group.id) {
      setExpandedGroupId(null);
      setMembers([]);
      setVectorSummary(null);
      setShowAnalysis(false);
      return;
    }
    setExpandedGroupId(group.id);
    const m = await loadGroupMembers(group.id);
    setMembers(m);
    setShowAnalysis(false);
    setVectorSummary(null);
  };

  const handleAddMember = async () => {
    if (!expandedGroupId || !addClientId) return;
    const ok = await addMember(expandedGroupId, addClientId);
    if (ok) {
      const m = await loadGroupMembers(expandedGroupId);
      setMembers(m);
      setAddClientId('');
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!expandedGroupId) return;
    await removeMember(memberId);
    const m = await loadGroupMembers(expandedGroupId);
    setMembers(m);
  };

  const handleAnalyze = async () => {
    if (!expandedGroupId) return;
    setAnalysisLoading(true);
    const summary = await getGroupVectorSummary(expandedGroupId);
    setVectorSummary(summary);
    setShowAnalysis(true);
    setAnalysisLoading(false);
  };

  // Filter clients not already in group
  const availableClients = clients.filter(
    c => !members.some(m => m.clientId === c.id)
  );

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Users className="w-4 h-4 text-primary" />
          Gruppenanalyse
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Neue Gruppe erstellen */}
        <div className="flex gap-2">
          <Input
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            placeholder="Neue Gruppe..."
            className="h-8 text-sm"
            onKeyDown={(e) => e.key === 'Enter' && handleCreateGroup()}
          />
          <Button size="sm" variant="outline" onClick={handleCreateGroup} disabled={!newGroupName.trim()}>
            <Plus className="w-3.5 h-3.5" />
          </Button>
        </div>

        {/* Gruppen-Liste */}
        {isLoading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
          </div>
        ) : groups.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-2">
            Noch keine Gruppen angelegt
          </p>
        ) : (
          <div className="space-y-2">
            {groups.map(group => (
              <div key={group.id} className="border border-border/50 rounded-md overflow-hidden">
                {/* Group header */}
                <button
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted/50 transition-colors"
                  onClick={() => handleExpand(group)}
                >
                  {expandedGroupId === group.id ? (
                    <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
                  )}
                  <div
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: group.color }}
                  />
                  <span className="font-medium truncate flex-1 text-left text-foreground">
                    {group.name}
                  </span>
                  <Badge variant="secondary" className="text-[10px] h-5">
                    {group.memberCount}
                  </Badge>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-6 w-6 shrink-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteGroup(group.id);
                    }}
                  >
                    <Trash2 className="w-3 h-3 text-destructive" />
                  </Button>
                </button>

                {/* Expanded content */}
                <AnimatePresence>
                  {expandedGroupId === group.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="px-3 pb-3 space-y-2 border-t border-border/30 pt-2">
                        {/* Add member */}
                        <div className="flex gap-1.5">
                          <Select value={addClientId} onValueChange={setAddClientId}>
                            <SelectTrigger className="h-7 text-xs flex-1">
                              <SelectValue placeholder="Klient wählen..." />
                            </SelectTrigger>
                            <SelectContent>
                              {availableClients.map(c => (
                                <SelectItem key={c.id} value={c.id} className="text-xs">
                                  {c.firstName} {c.lastName}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 px-2"
                            onClick={handleAddMember}
                            disabled={!addClientId}
                          >
                            <UserPlus className="w-3 h-3" />
                          </Button>
                        </div>

                        {/* Members */}
                        {members.length > 0 ? (
                          <div className="space-y-1">
                            {members.map(m => (
                              <div key={m.id} className="flex items-center justify-between text-xs px-1 py-0.5 rounded hover:bg-muted/30">
                                <span className="text-foreground">{m.firstName} {m.lastName}</span>
                                <Button
                                  size="icon"
                                  variant="ghost"
                                  className="h-5 w-5"
                                  onClick={() => handleRemoveMember(m.id)}
                                >
                                  <X className="w-2.5 h-2.5" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-[10px] text-muted-foreground">Keine Mitglieder</p>
                        )}

                        {/* Analyze button */}
                        {members.length >= 2 && (
                          <Button
                            size="sm"
                            variant="secondary"
                            className="w-full h-7 text-xs gap-1.5"
                            onClick={handleAnalyze}
                            disabled={analysisLoading}
                          >
                            {analysisLoading ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <BarChart3 className="w-3 h-3" />
                            )}
                            Vektor-Gruppenanalyse
                          </Button>
                        )}

                        {/* Analysis results */}
                        <AnimatePresence>
                          {showAnalysis && vectorSummary && (
                            <motion.div
                              initial={{ opacity: 0, y: -5 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0 }}
                              className="space-y-2 pt-1"
                            >
                              <div className="text-[10px] text-muted-foreground text-center">
                                Ø Gruppenprofil ({vectorSummary.memberCount} Klienten)
                              </div>

                              <RadarChart summary={vectorSummary} />

                              {/* Dimension averages */}
                              <div className="space-y-1">
                                {vectorSummary.dimensionLabels.map((label, i) => (
                                  <div key={i} className="flex items-center gap-2 text-xs">
                                    <div
                                      className="w-2 h-2 rounded-full shrink-0"
                                      style={{ backgroundColor: DIMENSION_COLORS[i] }}
                                    />
                                    <span className="text-muted-foreground flex-1">{label}</span>
                                    <span className="font-mono text-foreground">
                                      {vectorSummary.avgDimensions[i].toFixed(1)}
                                    </span>
                                  </div>
                                ))}
                              </div>

                              {/* Member list with phases */}
                              <div className="border-t border-border/30 pt-1.5 space-y-1">
                                <div className="text-[10px] text-muted-foreground">Individuelle Phasen</div>
                                {vectorSummary.members.map((m, i) => (
                                  <div key={i} className="flex items-center justify-between text-[11px]">
                                    <span className="text-foreground truncate">{m.name}</span>
                                    <Badge
                                      variant="outline"
                                      className="text-[9px] h-4"
                                      style={{
                                        borderColor: m.phase === 'stable' ? 'hsl(150, 70%, 45%)' :
                                          m.phase === 'transition' ? 'hsl(45, 80%, 50%)' : 'hsl(var(--primary))',
                                      }}
                                    >
                                      {m.phase}
                                    </Badge>
                                  </div>
                                ))}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
