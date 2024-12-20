#!/usr/bin/python3
import os
from PyQt5 import QtCore, QtWidgets, QtGui
import qasync
import fissure
from fissure.utils import plugin
from fissure.utils.common import PLUGIN_DIR
from fissure.Dashboard.Slots.LibraryTabSlots import _slotAttackImportProtocolChanged

def connect_plugins_slots(dashboard: QtCore.QObject):
    """Connect Plugins Slots

    Parameters
    ----------
    dashboard : QtCore.QObject
        FISSURE dashboard
    """
    dashboard.ui.pluginsPushButtonRefresh.clicked.connect(
        lambda: _slotSensorNodesPluginsPluginsListRefresh(dashboard)
    )
    dashboard.ui.pluginsPushButtonDeploy.clicked.connect(
        lambda: _slotSensorNodesPluginsDeploy(dashboard)
    )
    dashboard.ui.pluginsPushButtonRemove.clicked.connect(
        lambda: _slotSensorNodesPluginsRemove(dashboard)
    )
    dashboard.ui.pluginsPushButtonInstall.clicked.connect(
        lambda: _slotSensorNodesPluginsInstall(dashboard)
    )
    dashboard.ui.pluginsPushButtonUninstall.clicked.connect(
        lambda: _slotSensorNodesPluginsUninstall(dashboard)
    )


@qasync.asyncSlot(QtCore.QObject)
async def _slotSensorNodesPluginsPluginsListRefresh(dashboard: QtCore.QObject):
    """Refresh Sensor Node Plugins Table

    Parameters
    ----------
    dashboard : QtCore.QObject
        FISSURE dashboard
    """
    # gray all rows prior to requesting update
    table: QtWidgets.QTableWidget = dashboard.ui.pluginsTable
    table.horizontalHeader().setVisible(True) # set header visible in code; qt designer always sets to false
    for i in range(table.rowCount()):
        table.item(i, 0).setBackground(QtGui.QBrush(QtGui.QColor('gray')))
        table.item(i, 1).setBackground(QtGui.QBrush(QtGui.QColor('gray')))
        table.item(i, 2).setBackground(QtGui.QBrush(QtGui.QColor('gray')))

    # request update
    await dashboard.backend.checkPluginStatus(dashboard.active_sensor_node)


@qasync.asyncSlot(QtCore.QObject)
async def _slotSensorNodesPluginsDeploy(dashboard: QtCore.QObject):
    """Deploy Plugins to Sensor Node

    Parameters
    ----------
    dashboard : QtCore.QObject
        FISSURE dashboard
    """
    table: QtWidgets.QTableWidget = dashboard.ui.pluginsTable
    get_sensor_node = ['sensor_node1','sensor_node2','sensor_node3','sensor_node4','sensor_node5']
    transfer_plugins = []
    if dashboard.active_sensor_node > -1 and dashboard.backend.settings[get_sensor_node[dashboard.active_sensor_node]]['local_remote'] == 'remote':
        # get plugin names to transfer
        for item in [table.item(i,0) for i in range(table.rowCount())]:
            if item.isSelected():
                transfer_plugins += [item.text()]

        if len(transfer_plugins) > 0:
            # plugins exist to transfer
            await dashboard.backend.transferPlugins(dashboard.active_sensor_node, transfer_plugins)

            # refresh plugin table (transferred plugins may be installed on sensor node)
            await _slotSensorNodesPluginsPluginsListRefresh(dashboard)


@qasync.asyncSlot(QtCore.QObject)
async def _slotSensorNodesPluginsRemove(dashboard: QtCore.QObject):
    """Remove Plugin from Sensor Node

    Parameters
    ----------
    dashboard : QtCore.QObject
        FISSURE dashboard
    """
    table: QtWidgets.QTableWidget = dashboard.ui.pluginsTable
    get_sensor_node = ['sensor_node1','sensor_node2','sensor_node3','sensor_node4','sensor_node5']
    update = False
    if dashboard.active_sensor_node > -1 and dashboard.backend.settings[get_sensor_node[dashboard.active_sensor_node]]['local_remote'] == 'remote':
        # sensor node is remote, allow removal
        for item in [table.item(i,0) for i in range(table.rowCount())]:
            if item.isSelected():
                await dashboard.backend.removePlugin(dashboard.active_sensor_node, item.text())
                update = True
        if update:
            await _slotSensorNodesPluginsPluginsListRefresh(dashboard)


@qasync.asyncSlot(QtCore.QObject)
async def _slotSensorNodesPluginsInstall(dashboard: QtCore.QObject):
    """Install Plugins on Sensor Node

    Parameters
    ----------
    dashboard : QtCore.QObject
        FISSURE dashboard
    """
    table: QtWidgets.QTableWidget = dashboard.ui.pluginsTable
    plugin_names = []
    for item in [table.item(i,0) for i in range(table.rowCount())]:
        if item.isSelected():
            plugin_names += [item.text()]
    if len(plugin_names) > 0:
        if dashboard.backend.hiprfisr_connected is True:
            PARAMETERS = {
                "sensor_node_id": dashboard.active_sensor_node,
                "plugin_names": plugin_names
            }
            msg = {
                    fissure.comms.MessageFields.IDENTIFIER: fissure.comms.Identifiers.DASHBOARD,
                    fissure.comms.MessageFields.MESSAGE_NAME: "installPlugins",
                    fissure.comms.MessageFields.PARAMETERS: PARAMETERS,
            }
            await dashboard.backend.hiprfisr_socket.send_msg(fissure.comms.MessageTypes.COMMANDS, msg)


@qasync.asyncSlot(QtCore.QObject)
async def _slotSensorNodesPluginsUninstall(dashboard: QtCore.QObject):
    """Send Plugin Uninstall Command

    Parameters
    ----------
    dashboard : QtCore.QObject
        FISSURE dashboard
    """
    table: QtWidgets.QTableWidget = dashboard.ui.pluginsTable
    plugin_names = []
    for item in [table.item(i,0) for i in range(table.rowCount())]:
        if item.isSelected():
            plugin_names += [item.text()]
    if len(plugin_names) > 0:
        if dashboard.backend.hiprfisr_connected is True:
            PARAMETERS = {
                "sensor_node_id": dashboard.active_sensor_node,
                "plugin_names": plugin_names
            }
            msg = {
                    fissure.comms.MessageFields.IDENTIFIER: fissure.comms.Identifiers.DASHBOARD,
                    fissure.comms.MessageFields.MESSAGE_NAME: "uninstallPlugins",
                    fissure.comms.MessageFields.PARAMETERS: PARAMETERS,
            }
            await dashboard.backend.hiprfisr_socket.send_msg(fissure.comms.MessageTypes.COMMANDS, msg)