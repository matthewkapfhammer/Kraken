from kraken.core.maths import Vec3, Vec3, Euler, Quat, Xfo

from kraken.core.objects.components.component import Component

from kraken.core.objects.attributes.attribute_group import AttributeGroup
from kraken.core.objects.attributes.float_attribute import FloatAttribute
from kraken.core.objects.attributes.bool_attribute import BoolAttribute

from kraken.core.objects.constraints.pose_constraint import PoseConstraint

from kraken.core.objects.component_group import ComponentGroup
from kraken.core.objects.hierarchy_group import HierarchyGroup
from kraken.core.objects.locator import Locator
from kraken.core.objects.joint import Joint
from kraken.core.objects.ctrlSpace import CtrlSpace
from kraken.core.objects.control  import Control

from kraken.core.objects.operators.splice_operator import SpliceOperator

from kraken.core.profiler import Profiler
from kraken.helpers.utility_methods import logHierarchy


class FootComponentGuide(Component):
    """Foot Component Guide"""

    def __init__(self, name='Foot', parent=None, data=None):
        super(FootComponentGuide, self).__init__(name, parent)

        # ================
        # Setup Hierarchy
        # ================
        controlsLayer = self.getOrCreateLayer('controls')
        ctrlCmpGrp = ComponentGroup(self.getName(), self, parent=controlsLayer)

        # IO Hierarchies
        inputHrcGrp = HierarchyGroup('inputs', parent=ctrlCmpGrp)
        cmpInputAttrGrp = AttributeGroup('inputs', parent=inputHrcGrp)

        outputHrcGrp = HierarchyGroup('outputs', parent=ctrlCmpGrp)
        cmpOutputAttrGrp = AttributeGroup('outputs', parent=outputHrcGrp)


        # ===========
        # Declare IO
        # ===========
        # Declare Inputs Xfos
        self.legEndXfoInputTgt = self.createInput('legEndXfo', dataType='Xfo', parent=inputHrcGrp)
        self.legEndPosInputTgt = self.createInput('legEndPos', dataType='Xfo', parent=inputHrcGrp)

        # Declare Output Xfos
        self.footEndOutputTgt = self.createOutput('footEnd', dataType='Xfo', parent=outputHrcGrp)
        self.footOutputTgt = self.createOutput('foot', dataType='Xfo', parent=outputHrcGrp)

        # Declare Input Attrs
        self.drawDebugInputAttr = self.createInput('drawDebug', dataType='Boolean', parent=cmpInputAttrGrp)
        self.rightSideInputAttr = self.createInput('rightSide', dataType='Boolean', parent=cmpInputAttrGrp)

        # Declare Output Attrs

        # =========
        # Controls
        # =========
        # Guide Controls
        self.footCtrl = Control('foot', parent=ctrlCmpGrp, shape="sphere")

        if data is None:
            data = {
                    "name": name,
                    "location": "L",
                    "footXfo": Xfo(tr=Vec3(1.841, 1.1516, -1.237), ori=Quat(Vec3(0.6377, -0.5695, 0.3053), 0.4190))
                   }

        self.loadData(data)


    # =============
    # Data Methods
    # =============
    def saveData(self):
        """Save the data for the component to be persisted.

        Return:
        The JSON data object

        """

        data = {
            'name': self.getName(),
            'location': self.getLocation(),
            'footXfo': self.footCtrl.xfo
            }

        return data


    def loadData(self, data):
        """Load a saved guide representation from persisted data.

        Arguments:
        data -- object, The JSON data object.

        Return:
        True if successful.

        """

        if 'name' in data:
            self.setName(data['name'])

        self.setLocation(data['location'])
        self.footCtrl.xfo = data['footXfo']

        return True


    def getGuideData(self):
        """Returns the Guide data used by the Rig Component to define the layout of the final rig..

        Return:
        The JSON rig data object.

        """

        # values
        footXfo = self.footCtrl.xfo

        data = {
                "class":"kraken.examples.foot_component.FootComponent",
                "name": self.getName(),
                "location": self.getLocation(),
                "footXfo": footXfo
               }

        return data


class FootComponent(Component):
    """Foot Component"""

    def __init__(self, name='foot', parent=None):

        Profiler.getInstance().push("Construct Foot Component:" + name)
        super(FootComponent, self).__init__(name, parent)

        # ================
        # Setup Hierarchy
        # ================
        controlsLayer = self.getOrCreateLayer('controls')
        ctrlCmpGrp = ComponentGroup(self.getName(), self, parent=controlsLayer)

        # IO Hierarchies
        inputHrcGrp = HierarchyGroup('inputs', parent=ctrlCmpGrp)
        cmpInputAttrGrp = AttributeGroup('inputs', parent=inputHrcGrp)

        outputHrcGrp = HierarchyGroup('outputs', parent=ctrlCmpGrp)
        cmpOutputAttrGrp = AttributeGroup('outputs', parent=outputHrcGrp)


        # ===========
        # Declare IO
        # ===========
        # Declare Inputs Xfos
        self.legEndXfoInputTgt = self.createInput('legEndXfo', dataType='Xfo', parent=inputHrcGrp)
        self.legEndPosInputTgt = self.createInput('legEndPos', dataType='Xfo', parent=inputHrcGrp)

        # Declare Output Xfos
        self.footEndOutputTgt = self.createOutput('footEnd', dataType='Xfo', parent=outputHrcGrp)
        self.footOutputTgt = self.createOutput('foot', dataType='Xfo', parent=outputHrcGrp)

        # Declare Input Attrs
        self.drawDebugInputAttr = self.createInput('drawDebug', dataType='Boolean', parent=cmpInputAttrGrp)
        self.rightSideInputAttr = self.createInput('rightSide', dataType='Boolean', parent=cmpInputAttrGrp)

        # Declare Output Attrs


        # =========
        # Controls
        # =========
        # Foot
        self.footCtrlSpace = CtrlSpace('foot', parent=ctrlCmpGrp)

        self.footCtrl = Control('foot', parent=self.footCtrlSpace, shape="cube")
        self.footCtrl.alignOnXAxis()
        self.footCtrl.scalePoints(Vec3(2.5, 1.5, 0.75))

        # Rig Ref objects
        self.footRefSrt = Locator('footRef', parent=ctrlCmpGrp)

        # Add Component Params to IK control
        footSettingsAttrGrp = AttributeGroup("DisplayInfo_FootSettings",
            parent=self.footCtrl)
        footLinkToWorldInputAttr = FloatAttribute('linkToWorld', 1.0,
            maxValue=1.0, parent=footSettingsAttrGrp)


        # ==========
        # Deformers
        # ==========
        deformersLayer = self.getOrCreateLayer('deformers')
        defCmpGrp = ComponentGroup(self.getName(), self, parent=deformersLayer)

        footDef = Joint('foot', parent=defCmpGrp)
        footDef.setComponent(self)


        # ==============
        # Constrain I/O
        # ==============
        # Constraint inputs

        # Constraint outputs
        handConstraint = PoseConstraint('_'.join([self.footOutputTgt.getName(), 'To', self.footCtrl.getName()]))
        handConstraint.addConstrainer(self.footCtrl)
        self.footOutputTgt.addConstraint(handConstraint)

        handEndConstraint = PoseConstraint('_'.join([self.footEndOutputTgt.getName(), 'To', self.footCtrl.getName()]))
        handEndConstraint.addConstrainer(self.footCtrl)
        self.footEndOutputTgt.addConstraint(handEndConstraint)


        # ==================
        # Add Component I/O
        # ==================
        # Add Xfo I/O's
        # self.addInput(self.legEndXfoInputTgt)
        # self.addInput(self.legEndPosInputTgt)
        # self.addOutput(self.footOutputTgt)
        # self.addOutput(self.footEndOutputTgt)

        # Add Attribute I/O's
        # self.addInput(self.drawDebugInputAttr)
        # self.addInput(self.rightSideInputAttr)
        # self.addInput(footLinkToWorldInputAttr)


        # ===============
        # Add Splice Ops
        # ===============
        # Add Hand Solver Splice Op
        # spliceOp = SpliceOperator("footSolverSpliceOp", "HandSolver", "KrakenHandSolver")
        # self.addOperator(spliceOp)

        # # Add Att Inputs
        # spliceOp.setInput("drawDebug", self.drawDebugInputAttr)
        # spliceOp.setInput("rightSide", self.rightSideInputAttr)
        # spliceOp.setInput("linkToWorld", footLinkToWorldInputAttr)

        # # Add Xfo Inputs)
        # spliceOp.setInput("armEndXfo", legEndXfoInput)
        # spliceOp.setInput("armEndPos", legEndPosInput)
        # spliceOp.setInput("handRef", footRefSrt)

        # # Add Xfo Outputs
        # spliceOp.setOutput("handCtrlSpace", footCtrlSpace)


        # Add Deformer Splice Op
        spliceOp = SpliceOperator("footDeformerSpliceOp", "PoseConstraintSolver", "Kraken")
        self.addOperator(spliceOp)

        # Add Att Inputs
        spliceOp.setInput("drawDebug", self.drawDebugInputAttr)
        spliceOp.setInput("rightSide", self.rightSideInputAttr)

        # Add Xfo Inputs)
        spliceOp.setInput("constrainer", self.footOutputTgt)

        # Add Xfo Outputs
        spliceOp.setOutput("constrainee", footDef)

        Profiler.getInstance().pop()


    def loadData(self, data=None):

        self.setName(data.get('name', 'foot'))
        location = data.get('location', 'M')
        self.setLocation(location)

        self.footCtrlSpace.xfo = data['footXfo']
        self.footCtrl.xfo = data['footXfo']
        self.footRefSrt.xfo = data['footXfo']

        # ============
        # Set IO Xfos
        # ============
        self.legEndXfoInputTgt.xfo = data['footXfo']
        self.legEndPosInputTgt.xfo = data['footXfo']
        self.footEndOutputTgt.xfo = data['footXfo']
        self.footOutputTgt.xfo = data['footXfo']


from kraken.core.kraken_system import KrakenSystem
ks = KrakenSystem.getInstance()
ks.registerComponent(FootComponent)
ks.registerComponent(FootComponentGuide)
