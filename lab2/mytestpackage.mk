################################################################################
#
# mytestpackage
#
################################################################################

MYTESTPACKAGE_VERSION = 1.0
MYTESTPACKAGE_SITE = $(TOPDIR)/../customPackages/mytestpackage
MYTESTPACKAGE_SITE_METHOD = local

define MYTESTPACKAGE_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) mytestpackage -C $(@D)
endef

define MYTESTPACKAGE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/mytestpackage $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
