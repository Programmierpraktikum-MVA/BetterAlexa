/****************************************************************************
**
** Copyright (C) 2021 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the Qt Quick Controls 2 module of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:COMM$
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** $QT_END_LICENSE$
**
**
**
**
**
**
**
**
**
**
**
**
**
**
**
**
****************************************************************************/

import QtQuick 2.12
import HelperWidgets 2.0
import QtQuick.Layouts 1.12

Column {
    width: parent.width

    Section {
        width: parent.width
        caption: qsTr("TabBar")

        SectionLayout {
            Label {
                text: qsTr("Position")
                tooltip: qsTr("Position of the tabbar.")
            }
            SecondColumnLayout {
                ComboBox {
                    backendValue: backendValues.position
                    model: [ "Header", "Footer" ]
                    scope: "TabBar"
                    Layout.fillWidth: true
                }
            }

            Label {
                text: qsTr("Content Width")
                tooltip: qsTr("Content height used for calculating the total implicit width.")
            }
            SecondColumnLayout {
                SpinBox {
                    maximumValue: 9999999
                    minimumValue: -9999999
                    decimals: 0
                    backendValue: backendValues.contentWidth
                    Layout.fillWidth: true
                }
            }

            Label {
                text: qsTr("Content Height")
                tooltip: qsTr("Content height used for calculating the total implicit height.")
            }
            SecondColumnLayout {
                SpinBox {
                    maximumValue: 9999999
                    minimumValue: -9999999
                    decimals: 0
                    backendValue: backendValues.contentHeight
                    Layout.fillWidth: true
                }
            }
        }
    }

    ContainerSection {
        width: parent.width
    }

    ControlSection {
        width: parent.width
    }

    FontSection {
        width: parent.width
    }

    PaddingSection {
        width: parent.width
    }
}
