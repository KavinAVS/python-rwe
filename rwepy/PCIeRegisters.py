from enum import Enum

class PCIeRegisters(Enum):
    power_management_capability = 0x01
    pcie_express_capability = 0x10
    msi_capability = 0x05
    msix_capability = 0x11
    enhanced_allocation_capability_first_dw = 0x14
    fpb_capability = 0x15
    vendor_specific_capability = 0x09
    advanced_features_capability = 0x13
    subsystem_id_and_subsystem_vendor_id_capability = 0x0D 

class PCIeExtendedRegisters(Enum):
    secondary_pci_express_extended_capability = 0x0019
    data_link_feature_extended_capability = 0x0025
    physical_layer_160gts_entended_capability = 0x0026
    physical_layer_320gts_entended_capability = 0x002A
    physical_layer_640gts_entended_capability = 0x0031
    flit_logging_extended_capability = 0x0032
    device_3_extended_capability = 0x002F
    lane_margining_at_the_receiver_extended_capability = 0x0027
    acs_extended_capability = 0x000D
    power_budgeting_extended_capability = 0x0004
    ltr_extended_capability = 0x0018
    l1_pm_substates_extended_capability = 0x001E
    advanced_error_reporting_extended_capability = 0x0001
    resizable_bar_extended_capability = 0x0015
    vf_resizable_bar_extended_capability = 0x0024
    air_extended_capability = 0x000E
    pasid_extended_capability = 0x001B
    frs_queueing_extended_capability = 0x0021
    flit_error_injection_extended_capability = 0x0034
    virtual_channel_extended_capability = 0x0002
    multi_function_virtual_channel_extended_capability = 0x0008
    device_serial_number_extended_capability = 0x0003
    vendor_specific_extended_capability = 0x000B
    designated_vendor_specific_extended_capability = 0x0023
    rcrb_header_extended_capability = 0x000A
    root_complex_link_declaration_extended_capability = 0x0005
    root_complex_internal_link_control_extended_capability = 0x0006
    root_complex_event_collector_endpoint_association_extended_capability  = 0x0007
    multicast_extended_capability = 0x0012
    dpa_extended_capability = 0x0016
    tph_requester_extended_capability = 0x0017
    dpc_extended_capability = 0x001D
    ptm_extended_capability = 0x001F
    readiness_time_reporting_extended_capability = 0x0022
    hierarchy_id_extended_capability = 0x0028
    native_pcie_enclosure_management_extended_capability = 0x0029
    alternate_protocol_extended_capability = 0x002B
    sfi_extended_capability = 0x002C
    data_object_exchange_extended_capability = 0x002E
    shadow_functions_extended_capability = 0x002D
    ide_extended_capability = 0x0030





