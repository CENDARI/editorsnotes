<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output 
method="text"
encoding="utf-8"
omit-xml-declaration="yes"
standalone="no"
media-type="text/plain"/>

  <xsl:template match="hi[@rend='bold']">
    <xsl:text>__</xsl:text><xsl:apply-templates/><xsl:text>__</xsl:text>
  </xsl:template>

  <xsl:template match="hi[@rend='italics']">
    <xsl:text>''</xsl:text><xsl:apply-templates/><xsl:text>''</xsl:text>
  </xsl:template>

  <xsl:template match="hi[@rend='underline']">
    <xsl:text>===</xsl:text><xsl:apply-templates/><xsl:text>===</xsl:text>
  </xsl:template>

  <xsl:template match="note">
    <xsl:text>[</xsl:text><xsl:apply-templates/><xsl:text>]</xsl:text>
  </xsl:template>

  <xsl:template match="div[head]">
    <xsl:variable name="depth" select="count(ancestor::*)"/>
    <xsl:for-each select="1 to $depth">!</xsl:for-each>
  </xsl:template>

  <xsl:template match="div/head">
      <xsl:apply-templates/><xsl:text>
</xsl:text>
  </xsl:template>

  <xsl:template match="*">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
